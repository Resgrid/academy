#!/bin/sh
# Preserve the inherited public Mapbox key. Never print environment values.
set -eu
support_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
recording_dir=${RESPONDER_RECORDING_DIR:-"$support_dir/../../../../capture-apps/Responder"}
: "${RESPOND_MAPBOX_PUBKEY:?The inherited public Mapbox key is required}"
cd "$recording_dir"
export APP_ENV=development EXPO_NO_DOTENV=1 EXPO_NO_TELEMETRY=1 DO_NOT_TRACK=1 CI=1 BROWSER=none EXPO_OFFLINE=1
export RESPOND_BASE_API_URL=http://127.0.0.1:18967 RESPOND_API_VERSION=v4 RESPOND_RESGRID_API_URL=/api/v4
export RESPOND_CHANNEL_API_URL=http://127.0.0.1:18967/
export RESPOND_COUNTLY_APP_KEY='' RESPOND_COUNTLY_URL='' RESPOND_SENTRY_DSN='' RESPOND_LOGGING_KEY=''
# Metro's --no-dev mode omitted the web stylesheet; production captures must use
# a full Expo static export rather than dropping CSS injection on this dev server.
exec node node_modules/expo/bin/cli start --web --localhost --port "${RESPONDER_RECORDING_PORT:-19102}" --clear
