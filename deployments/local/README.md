# Plane on a LAN server

This deployment builds the fork's production applications and serves everything through one HTTP port, **17239**. PostgreSQL, Valkey, RabbitMQ and RustFS communicate over the Compose network. No infrastructure ports are published.

## First installation

Prerequisites: Linux x86-64, Docker Engine with the Compose plugin, Git, and internet access to download images and build dependencies. Run these commands from the repository root:

```sh
cp .env.local.example .env
```

Edit this single `.env`:

- Set `WEB_URL` to the address browsers will use, including the port and no trailing slash. For the LAN server: `http://10.147.19.203:17239`.
- Keep `LISTEN_HTTP_PORT=17239`, or change both it and the port in `WEB_URL`.
- Generate `SECRET_KEY` and `LIVE_SERVER_SECRET_KEY` separately using `openssl rand -hex 32`. Save each output in its corresponding variable. Keep these values unchanged across upgrades.
- Leave the remaining defaults unless you need an override. Use URL-safe characters in database and RabbitMQ credentials because Compose includes them in connection URLs.

Start the entire installation:

```sh
docker compose -f docker-compose-local.yml up -d --build
```

The initial build can take a while. Compose prepares persistent directories, waits for infrastructure health, applies database migrations, starts the API and creates the S3 bucket before opening the proxy. There is no need to run `setup.sh`, install pnpm on the host, or maintain any `apps/*/.env` files.

Open `WEB_URL` in your browser. Instance administration is at `/god-mode/`; use the browser's initial setup flow to create the instance administrator. Then create your workspace through the main app. Public project views use `/spaces/`, collaboration uses `/live/`, and file uploads use the same host and port.

## Accounts and optional email

Email/password signup is enabled by default; SMTP and magic-link login are not required for initial setup. With SMTP absent, email delivery, emailed invitations and password-reset messages are unavailable. Users can register directly, then use the app's workspace invitation/join flow. Configure SMTP in instance administration when email delivery is needed.

The optional `EMAIL_*` values in `.env` seed the instance on its first start. After initialization, Plane stores these settings in PostgreSQL; edit them through `/god-mode/` rather than expecting environment edits to overwrite saved settings.

## Persistent files

`DATA_DIR` defaults to `./data`, relative to this repository:

| Folder                     | Content                                      |
| -------------------------- | -------------------------------------------- |
| `postgres/`                | Database records and instance settings       |
| `rustfs/data/`             | Uploaded objects and storage metadata        |
| `rustfs/logs/`             | Storage logs                                 |
| `redis/`                   | Valkey append-only persistence               |
| `rabbitmq/`                | Queue state, with a stable RabbitMQ hostname |
| `beat/`                    | Periodic task schedule                       |
| `logs/`                    | API, worker and migration logs               |
| `proxy/`, `web/`, `admin/` | Caddy configuration/state                    |

Compose creates these directories automatically. RustFS's initialization container sets ownership on its two directories. Containers use different numeric owners; this is expected. `data/` and `.env` are ignored by Git and excluded from application build contexts. If you choose an alternative `DATA_DIR`, prefer an absolute path outside the repository so builds cannot include it.

Container recreation and `docker compose down` preserve these bind-mounted directories. Keep `.env` with backups: losing or changing `SECRET_KEY` can make stored configuration unreadable. For a consistent simple backup, stop this Compose stack and copy `.env` and all of `DATA_DIR`, preserving file ownership.

## Updates and diagnostics

```sh
git pull --ff-only
docker compose -f docker-compose-local.yml up -d --build
docker compose -f docker-compose-local.yml ps -a
docker compose -f docker-compose-local.yml logs --tail=100 api migrator plane-rustfs
```

Check that `migrator` and `rustfs-init` exited with status 0 and long-running services are running. The same startup command is safe to repeat; existing records and uploaded files remain. Frontend assets are built with relative browser URLs, so changing the public address does not bake Docker hostnames into the browser bundle. Recreate containers after changing `.env`.

The legacy `USE_MINIO=1` variable is deliberately set internally: Plane uses that switch for S3-compatible storage and same-origin signed URLs, including RustFS. It does not start or download MinIO. RustFS is pinned to `1.0.0-rc.6`; storage image upgrades should be deliberate.

Run deployment contract checks without starting containers:

```sh
python3 -m unittest discover -s deployments/local/tests -v
```

With the stack running, include the HTTP burst regression check:

```sh
PLANE_SMOKE_URL=http://localhost:17239 python3 -m unittest discover -s deployments/local/tests -v
pnpm --filter space test:unit
```

The local web/admin Caddy configuration allows the large asset bursts generated by the frontend. The public-pages server uses an internal runtime API address for metadata while browser requests stay on the public origin.

This file replaces the previous backend-only local Compose setup. The root `docker-compose.yml`, test stack, and development `setup.sh` remain separate workflows.
