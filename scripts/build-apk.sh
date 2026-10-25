#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/android-env.sh
python3 scripts/prepare-android.py
if [ ! -f platforms/android/cordova/Api.js ]; then
  npx --no-install cordova platform add android@13.0.0 --nosave --no-telemetry
fi
npx --no-install cordova build android --debug --no-telemetry -- --packageType=apk --gradleArg=--no-daemon --gradleArg=--max-workers=2
mkdir -p builds
cp platforms/android/app/build/outputs/apk/debug/app-debug.apk builds/School-Nowell-debug.apk
"$ANDROID_SDK_ROOT/build-tools/34.0.0/apksigner" verify --verbose builds/School-Nowell-debug.apk
sha256sum builds/School-Nowell-debug.apk > builds/School-Nowell-debug.apk.sha256
