# LAN deployment implementation plan

**Goal:** Build this fork and run all Plane interfaces on one HTTP port, with one root `.env` and persistent host directories.

**Approved scope:** Fresh installation, RustFS instead of MinIO, port 17239, browser onboarding without SMTP, production builds. Validate on this workstation before pushing to GitHub and rebuilding on the LAN server. No migration, HTTPS, infrastructure consoles, or hot reload.

**Architecture:** Keep the production Dockerfiles and route web, admin, space, API, live and S3 through Caddy. Compose supplies internal addresses, orders healthy dependencies and migrations, and initializes RustFS directory ownership automatically. Public browser URLs use the same origin; the space server and live server reach the API internally.

## Tasks

- [x] Add a deployment contract test using `docker compose config --format json`; verify missing services, extra published ports and nonpersistent mounts fail against the old configuration.
- [x] Replace `docker-compose-local.yml` with production services, health checks, migration gating, persistent bind mounts and RustFS. Add a local Caddy config and root environment template; exclude data and nested environment files from Docker contexts.
- [x] Run contract tests, build locally, start from empty data, and verify browser administrator setup, accounts, work items, public pages, uploads, live connections and container recreation.
- [x] Document first boot, SMTP limitations, updates, persistence and commands in `deployments/local/README.md`.
- [x] Review and commit the verified changes, push the working branch to GitHub, pull that branch on the server without modifying unrelated files, and rebuild/test there.

## Verification

Run `python3 -m unittest discover -s deployments/local/tests -v`, then `docker compose -f docker-compose-local.yml up -d --build`. Check `ps -a`, service logs and HTTP routes. Use Playwright for actual browser flows. Keep local test credentials in ignored files only. Recreate containers and verify the same database records and uploaded bytes remain. Record actual outcomes and limitations below before declaring completion.

Implementation also fixes local static-file throttling and server-side public metadata URLs. See `deployments/local/VERIFICATION.md` for observed test results.
