#!/usr/bin/env bash
# Source this file; all downloaded tools and caches stay outside the checkout.
export NOWELL_ANDROID_TOOLS="${NOWELL_ANDROID_TOOLS:-/workspace/.nowell-tools}"
export ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$NOWELL_ANDROID_TOOLS/android-sdk}"
export ANDROID_HOME="$ANDROID_SDK_ROOT"
export ANDROID_USER_HOME="${ANDROID_USER_HOME:-$NOWELL_ANDROID_TOOLS/android-user}"
export GRADLE_USER_HOME="${GRADLE_USER_HOME:-$NOWELL_ANDROID_TOOLS/gradle-user}"
export npm_config_cache="${npm_config_cache:-$NOWELL_ANDROID_TOOLS/npm-cache}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$NOWELL_ANDROID_TOOLS/xdg-config}"
export JAVA_HOME="${JAVA_HOME:-$NOWELL_ANDROID_TOOLS/jdk-17.0.21+9}"
export PATH="$JAVA_HOME/bin:$NOWELL_ANDROID_TOOLS/gradle-8.7/bin:$ANDROID_SDK_ROOT/cmdline-tools/12.0/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH"
if [ -f "$NOWELL_ANDROID_TOOLS/java-network.env" ]; then
  source "$NOWELL_ANDROID_TOOLS/java-network.env"
fi
