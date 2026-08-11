# log-server

A single-purpose HTTP log server.

It accepts one file per POST. If `X-File-Path` contains subdirectories, those directories are created automatically.

## Run

```bash
python server.py --port 8000
```

Files are stored in `uploads/`.

Windows one-click startup:

```bat
start.bat
start.bat 9000
```

The script uses UTF-8 code page so Chinese paths are not garbled in the console.

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
