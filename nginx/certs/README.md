# TLS Certificates

This directory holds the TLS certificate and private key used by the Nginx
reverse-proxy container. **Real certificate files must never be committed**
(`.pem` / `.key` are listed in the repository `.gitignore`).

## Required files

The Nginx config (`nginx/nginx.conf`) expects exactly these two files:

```
nginx/certs/fullchain.pem   # full certificate chain
nginx/certs/privkey.pem     # corresponding private key
```

If your CA delivers the chain under different names (e.g. Tencent / Aliyun
issue `*.crt` + `*.key`, Let's Encrypt issues `fullchain.pem` + `privkey.pem`),
just rename or symlink them to the names above.

## How to upload (manual flow)

```bash
# from your local machine
scp fullchain.pem privkey.pem  user@server:/path/to/MCC-GCN-App/nginx/certs/

# on the server
chmod 600 nginx/certs/privkey.pem
docker compose restart nginx
```

## File-permission tips

- `privkey.pem` should be `0600` (owner read-only).
- The Nginx container runs as `root` inside, so it can read both files
  regardless of host UID, but keeping the key tight protects against host-side
  leaks.

## Renewal

There is no auto-renewal in this repo. Two common options:

1. **DNS-01 + manual upload** — easiest for one-off domains; replace both
   files and run `docker compose restart nginx`.
2. **HTTP-01 webroot** — Nginx already exposes
   `/.well-known/acme-challenge/` over plain HTTP. Point a Certbot webroot at
   a shared volume mounted to `/var/www/certbot` if you decide to automate.
