#!/bin/sh
# ==============================================================================
# KSP Sentinel AI — Production AppSail POSIX Startup & WSGI Execution
# ==============================================================================
# Adheres to POSIX standard /bin/sh (compatible with Dash, Bash, Busybox, Alpine)
# Performs non-destructive pre-flight environment checks before launching Gunicorn
# ==============================================================================
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "[KSP] Startup directory resolved to: $APP_DIR"
cd "$APP_DIR"

# 0. Bundled Vendor Resolution (Instant zero-network boot)
export PYTHONPATH="$APP_DIR/packages:$PYTHONPATH"
export PATH="$APP_DIR/packages/bin:$HOME/.local/bin:$PATH:/usr/local/bin"


# 1. Pre-flight Environment Validation (Fail-Fast Guard)
if [ -z "$KSP_PROJECT_ID" ]; then
    echo "[KSP] WARNING: KSP_PROJECT_ID environment variable is unset. Defaulting to Catalyst context." >&2
fi

if [ -z "$ZOHO_REFRESH_TOKEN_QUICKML" ]; then
    echo "[KSP] WARNING: ZOHO_REFRESH_TOKEN_QUICKML is unset. QuickML cloud predictions may require dynamic bootstrap." >&2
fi

# 2. Strict Port Resolution Contract
if [ -n "${X_ZOHO_CATALYST_LISTEN_PORT:-}" ]; then
    LISTEN_PORT="${X_ZOHO_CATALYST_LISTEN_PORT}"
elif [ -n "${PORT:-}" ]; then
    LISTEN_PORT="${PORT}"
else
    LISTEN_PORT="9000"
fi

# 3. Fail-Fast Validation
case "${LISTEN_PORT}" in
    ''|*[!0-9]*)
        echo "[KSP][FATAL] Invalid listen port resolved: ${LISTEN_PORT}"
        exit 1
        ;;
esac

echo "[KSP] --- Boot Environment Resolution ---"
echo "[KSP] X_ZOHO_CATALYST_LISTEN_PORT=${X_ZOHO_CATALYST_LISTEN_PORT:-<unset>}"
echo "[KSP] PORT=${PORT:-<unset>}"
echo "[KSP] Final LISTEN_PORT=${LISTEN_PORT}"
echo "[KSP] -----------------------------------"

# 4. Production WSGI Launch with Dynamic PATH & Module Resolution
export PATH="$APP_DIR/packages/bin:$HOME/.local/bin:$PATH:/usr/local/bin:/catalyst/.venv/bin:/catalyst/bin"

if python3 -c "import gunicorn" 2>/dev/null; then
    echo "[KSP] Found gunicorn module. Launching WSGI server on port ${LISTEN_PORT}..."
    exec python3 -m gunicorn --bind "0.0.0.0:${LISTEN_PORT}" --workers 1 --threads 8 --timeout 120 server:app
elif command -v gunicorn >/dev/null 2>&1; then
    echo "[KSP] Found gunicorn binary. Launching on port ${LISTEN_PORT}..."
    exec gunicorn --bind "0.0.0.0:${LISTEN_PORT}" --workers 1 --threads 8 --timeout 120 server:app
else
    echo "[KSP] Launching server.py natively on port ${LISTEN_PORT}..."
    exec python3 server.py
fi
