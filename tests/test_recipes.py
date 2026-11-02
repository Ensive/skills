"""Execute the documented recipes, with synthetic schema/handler dependencies.

Node type stripping checks behavior here, not TypeScript types or Zod integration.
"""
import re
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def recipe(skill, marker):
    blocks = re.findall(r"```typescript\n(.*?)\n```", (ROOT / skill / "SKILL.md").read_text(), re.S)
    return next(block for block in blocks if marker in block)


@unittest.skipUnless(shutil.which("node"), "Node 22.6+ unavailable")
class RecipeTests(unittest.TestCase):
    def run_recipe(self, source):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'recipe.ts'
            path.write_text(source)
            return subprocess.run(['node', '--experimental-strip-types', str(path)],
                                  capture_output=True, text=True, timeout=9)

    def test_model_facing_errors_never_echo_handler_or_validation_values(self):
        source = recipe('tool-registry-architect', 'export class ToolRegistry')
        driver = r'''
import assert from "node:assert/strict";
const secret = "SYNTHETIC_CREDENTIAL_813";
const registry = new ToolRegistry(new Set(["read"]));
const ctx = {signal:new AbortController().signal, granted:new Set(["read"]),
  workspaceRoot:"/synthetic", toolCallId:"fixture", logger:{info(){}}};
let calls = 0;
const base = {description:"synthetic", capabilities:new Set(["read"]), timeoutMs:20,
  schema:{safeParse:(data)=>({success:true,data})}};
for (const [name, value] of [["error", new Error(secret)], ["string", secret], ["object", {secret}]]) {
  registry.register({...base, name, handler:async()=>{calls++; throw value;}});
  const result = await registry.run(name, {}, ctx);
  assert.equal(result.isError, true);
  assert.equal(JSON.parse(result.content).error, "internal");
  assert.ok(!result.content.includes(secret));
}
registry.register({...base, name:"invalid", schema:{safeParse:()=>({success:false,error:{message:secret}})},
  handler:async()=>{calls++; return secret;}});
assert.equal(JSON.parse((await registry.run("invalid", {}, ctx)).content).error, "invalid_input");
assert.ok(!(await registry.run("invalid", {}, ctx)).content.includes(secret));
assert.ok(!(await registry.run(secret, {}, ctx)).content.includes(secret));
assert.equal(JSON.parse((await registry.run("error", {}, {...ctx,granted:new Set()})).content).error,"forbidden");
assert.equal(calls, 3);
registry.register({...base, name:"slow", handler:(_,ctx)=>new Promise((_,reject)=>
  ctx.signal.addEventListener("abort",()=>reject(new Error(secret)),{once:true}))});
assert.equal(JSON.parse((await registry.run("slow", {}, ctx)).content).error,"timeout");
const cancelled = new AbortController(); cancelled.abort(secret);
assert.equal(JSON.parse((await registry.run("slow", {}, {...ctx,signal:cancelled.signal})).content).error,"cancelled");
registry.register({...base,name:"ok",handler:async()=>"synthetic result"});
assert.equal((await registry.run("ok",{},ctx)).content,"synthetic result");
console.log("public errors, authorization, cancellation and success passed");
'''
        result = self.run_recipe(source + '\n' + driver)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(os.name == 'posix', 'POSIX signals unavailable')
    def test_signal_exit_codes_for_cooperative_and_stuck_cleanup(self):
        source = recipe('typescript-cli-architect', 'const ac = new AbortController')
        boundary = recipe('typescript-cli-architect', 'async function main()')
        for sig, expected in [('SIGINT', 130), ('SIGTERM', 143)]:
            for cooperative in [True, False]:
                with self.subTest(signal=sig, cooperative=cooperative):
                    # Run the shown top-level catch too: an abort rejection must not overwrite 130/143.
                    main = boundary.replace('/* ... */', '''
  await new Promise((_,reject)=>ac.signal.addEventListener("abort",()=>{
    clearInterval(keepAlive); reject(new Error("synthetic abort"));
  },{once:true}));''') if cooperative else ''
                    driver = f'const keepAlive=setInterval(()=>{{}},50);\n{main}\nsetImmediate(()=>process.kill(process.pid,"{sig}"));'
                    result = self.run_recipe(source + '\n' + driver)
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
