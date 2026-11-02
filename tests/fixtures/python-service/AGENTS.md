# Synthetic Python AI service

Use service/app.py and its app factory. Domain input is synthetic. Keep provider access injected; no credentials or live API calls. No Node modules, CLI scaffolding or Kubernetes are needed. From this directory run `python3 -m unittest discover -s tests -v`. FastAPI and HTTPX versions are in requirements-test.txt; use an isolated environment if installing them.

In-process ASGI tests do not prove network disconnect/reconnect behavior. Preserve that distinction in reports.
