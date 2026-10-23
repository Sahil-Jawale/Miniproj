# Automated Docker Container Deployment Using GitHub Actions and Docker Hub

Every push to `main` is automatically **tested → built into a Docker image → pushed to Docker Hub → deployed** as a running container on a self-hosted runner, with no manual steps.

## Architecture

```
Developer ──git push──▶ GitHub repo
                            │ triggers
                            ▼
                 GitHub Actions workflow
   ┌──────────────── GitHub-hosted (ubuntu-latest) ───────────────┐
   │  Job 1: test            pytest                               │
   │  Job 2: build-and-push  docker build → push to Docker Hub    │
   └──────────────────────────────────────────────────────────────┘
                            │                      │ image
                            ▼                      ▼
   ┌──────── Self-hosted runner (laptop) ────┐   Docker Hub
   │  Job 3: deploy                          │◀── docker pull
   │  stop old container → run new one       │
   │  health check on /health                │
   └─────────────────────────────────────────┘
                            ▼
                   http://localhost:5000
```

## Project structure

```
app/__init__.py              Flask app (routes / and /health)
app/templates/index.html     Page showing the message + deployed commit
tests/test_app.py            Unit tests (pytest)
Dockerfile                   Production image (gunicorn, non-root, healthcheck)
docker-compose.yml           Local run
.github/workflows/deploy.yml The CI/CD pipeline
```

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -v
flask --app app run          # http://localhost:5000
```

Or with Docker: `docker compose up --build`

## One-time setup

### 1. Docker Hub
1. Sign up at https://hub.docker.com
2. **Account Settings → Personal access tokens → Generate new token** (Read & Write). Copy it.

### 2. GitHub repository
1. Create a **private** repo (see Security note below) and push this folder to it.
2. **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | your Docker Hub username |
| `DOCKERHUB_TOKEN` | the access token from step 1 |

### 3. Self-hosted runner (your laptop)
1. **Settings → Actions → Runners → New self-hosted runner → Windows (x64)**.
2. Run the shown commands in PowerShell in a folder like `C:\actions-runner` (outside OneDrive).
3. During `config.cmd`, accept the defaults. When asked *"run as service?"* answer **N**.
4. Start it with `.\run.cmd` and leave the window open. It should show **Listening for Jobs**.
5. Make sure **Docker Desktop is running**.

> Why not as a service? A service runs as `NETWORK SERVICE`, which can't talk to Docker Desktop. Running `run.cmd` uses your user account, which can.

## Demo

1. Open http://localhost:5000 and note the message and commit.
2. Edit `MESSAGE` in `app/__init__.py` (e.g. `"Version 2 ..."`), then commit and push.
3. Watch the **Actions** tab: test → build-and-push → deploy.
4. Check the new tag on Docker Hub.
5. Refresh the page and the new message and commit SHA appear.
6. **Failure demo:** break a test and push. The pipeline stops at `test`, and the running app is untouched.

**Rollback:** run an older tag manually:
```powershell
docker rm -f flask-app
docker run -d --name flask-app -p 5000:5000 <user>/flask-cicd-demo:<old-sha>
```

## Security notes
- Credentials live only in GitHub Secrets, and Docker Hub is accessed with a token instead of a password.
- Images are tagged with the commit SHA, so every deployment can be traced and rolled back.
- The container runs as a non-root user and has a health check.
- **Use a private repo.** In a public repo, anyone's pull request could run code on your laptop through the self-hosted runner.

## Troubleshooting
- **`CERTIFICATE_VERIFY_FAILED` during a local `docker build`:** Avast's *HTTPS scanning* intercepts traffic inside containers. Disable it under *Avast → Settings → Protection → Core Shields → Web Shield → Enable HTTPS scanning*, or pause Web Shield while building. This doesn't affect the pipeline, because images are built on GitHub's servers.
- **Deploy job stuck on "Waiting for a runner":** `run.cmd` isn't running, or the runner is offline.
- **Port 5000 in use:** change `HOST_PORT` in the workflow.
