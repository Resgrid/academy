#!/bin/sh
# Keeps all inherited map credentials untouched. Values are never echoed.
set -eu
support_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
recording_dir=${IC_RECORDING_DIR:-"$support_dir/../../../../../capture-apps/IC"}
cd "$recording_dir"
export APP_ENV=development EXPO_NO_DOTENV=1 EXPO_NO_TELEMETRY=1 DO_NOT_TRACK=1 CI=1 BROWSER=none
export IC_BASE_API_URL=http://127.0.0.1:18967 IC_API_VERSION=v4 IC_RESGRID_API_URL=/api/v4
export IC_COUNTLY_APP_KEY='' IC_COUNTLY_SERVER_URL='' IC_SENTRY_DSN='' IC_LOGGING_KEY=''
exec node node_modules/expo/bin/cli start --web --localhost --clear --port "${IC_RECORDING_PORT:-19104}"
