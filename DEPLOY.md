# Clavis Home Server Deployment

## Routing

Production traffic is intended to flow through Cloudflare Tunnel into the compose-local nginx:

```text
cloudflared -> clavisapi.store -> localhost:8002 -> clavis_nginx -> clavis_web:8000
```

TLS is handled by Cloudflare. The nginx container listens on plain HTTP inside the home server and is bound only to `127.0.0.1:8002`, so it is not directly exposed on the LAN or public interface.

## Environment

Create the real env file from the template and keep it out of Git:

```bash
cp .env.example .env
```

Use these production values unless you intentionally keep PostgreSQL outside this compose stack:

```text
DJANGO_SETTINGS_MODULE=Clavis.settings.prod
POSTGRES_HOST=db
SECURE_SSL_REDIRECT=False
ALLOWED_HOSTS=clavisapi.store,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://clavisapi.store
```

## Deploy

Validate the compose file:

```bash
docker-compose -f docker-compose.prod.yml config
```

Build and start:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

Check container state:

```bash
docker-compose -f docker-compose.prod.yml ps
```

## ARC Quiz Content

ARC episode assets are not moved through Git. Copy them to the home server inside this repository:

```text
Clavis_TheCode_Server/
  ARC_Quiz/
```

The seed manifest is:

```text
ARC_Quiz/arc.json
```

From this repository, the compose files mount it read-only into the web container:

```text
./ARC_Quiz:/app/ARC_Quiz:ro
```

Copy from the Windows dev machine with `scp`, replacing the user and host:

```powershell
scp -r C:\Dev\project\TheCode\ARC_Quiz user@home-server:/path/to/deploy-parent/
```

Or from the home server, after placing the files by USB/SFTP/etc., verify:

```bash
ls -la ARC_Quiz
test -f ARC_Quiz/arc.json
```

After the stack is running, validate the manifest and source images:

```bash
docker-compose -f docker-compose.prod.yml run --rm web \
  python TheCode/manage.py seed_pie ARC_Quiz/arc.json --dry-run
```

Then seed or refresh the episode data and local media:

```bash
docker-compose -f docker-compose.prod.yml run --rm web \
  python TheCode/manage.py seed_pie ARC_Quiz/arc.json
```

The seed command copies the question images into:

```text
TheCode/media/stages/arc/001/
```

Nginx serves them through:

```text
https://clavisapi.store/media/stages/arc/001/...
```

## Cloudflare Tunnel

Point the Cloudflare Tunnel public hostname for `clavisapi.store` to:

```text
http://localhost:8002
```

For a file-based tunnel config, the relevant ingress rule is:

```yaml
ingress:
  - hostname: clavisapi.store
    service: http://localhost:8002
  - service: http_status:404
```

Then reload or restart the existing tunnel service:

```bash
sudo systemctl restart cloudflared
```

## Data Migration

If the current production database is still on AWS, dump it before switching DNS or tunnel routing:

```bash
pg_dump "$OLD_DATABASE_URL" > clavis-prod.sql
```

Start only the new PostgreSQL container:

```bash
docker-compose -f docker-compose.prod.yml up -d db
```

Restore into the home server database:

```bash
cat clavis-prod.sql | docker exec -i clavis_db sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'
```

Then start the full stack:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f db
```

## Verification

From the home server:

```bash
curl -I http://127.0.0.1:8002/
```

From outside the home server:

```bash
curl -I https://clavisapi.store/
```
