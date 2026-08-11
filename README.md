# log-server

A single-purpose HTTP log server.

It accepts one file per POST. If `X-File-Path` contains subdirectories, those directories are created automatically.

## Run

```bash
python server.py --port 9101
```

Files are stored in `uploads/`.

Windows one-click startup:

```bat
start.bat
start.bat 9101
start.bat 9101 D:\logs
```

To open the firewall port separately:

```bat
allow-firewall.bat
allow-firewall.bat 9101
```

The default port is `9101`. `start.bat` automatically opens the TCP firewall port when run with administrator permission.
The script uses UTF-8 code page so Chinese paths are not garbled in the console.
The default upload directory is `uploads\` under this repository. You can override it with the second argument.

## Public URL

To expose the server to external users with a temporary public URL:

```bat
tunnel.bat
```

`tunnel.bat` downloads `cloudflared` automatically, starts the local server, and prints a URL like:

```text
https://xxxx.trycloudflare.com
```

External users can upload logs to that URL. The URL is temporary and changes each time `tunnel.bat` runs.

Chinese paths can be sent URL-encoded:

```bash
curl -X POST \
  -H "X-File-Path: %E8%AE%BE%E5%A4%87/%E6%97%A5%E5%BF%97/app.log" \
  --data-binary @app.log \
  http://localhost:8000/upload
```

## Upload

```bash
curl -X POST \
  -H "X-File-Path: device-01/2026-08-11/app.log" \
  --data-binary @app.log \
  http://localhost:8000/upload
```

Result:

```text
uploads/device-01/2026-08-11/app.log
```

## Health

```bash
curl http://localhost:8000/health
```

Path traversal is rejected. There are no third-party dependencies.
