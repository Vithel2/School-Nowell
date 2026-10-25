#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/android-env.sh
mkdir -p "$NOWELL_ANDROID_TOOLS/downloads" "$ANDROID_USER_HOME" "$GRADLE_USER_HOME"
python3 - <<'PY'
import hashlib, os, pathlib, subprocess, tarfile, zipfile
tools = pathlib.Path(os.environ['NOWELL_ANDROID_TOOLS'])
downloads = tools / 'downloads'
jdk = downloads / 'OpenJDK17U-jdk_x64_linux_hotspot_17.0.21_9.tar.gz'
base = 'https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.21%2B9/'
if not jdk.exists():
    subprocess.run(['curl', '-fL', '--retry', '3', base + jdk.name, '-o', str(jdk)], check=True)
jdk_checksum = downloads / (jdk.name + '.sha256.txt')
if not jdk_checksum.exists():
    subprocess.run(['curl', '-fL', '--retry', '3', base + jdk_checksum.name, '-o', str(jdk_checksum)], check=True)
assert hashlib.sha256(jdk.read_bytes()).hexdigest() == jdk_checksum.read_text().split()[0], 'JDK checksum mismatch'
if not (tools / 'jdk-17.0.21+9/bin/javac').exists():
    with tarfile.open(jdk) as archive:
        archive.extractall(tools, filter='data')
gradle = downloads / 'gradle-8.7-bin.zip'
if not gradle.exists():
    subprocess.run(['curl', '-fL', '--retry', '3', 'https://services.gradle.org/distributions/gradle-8.7-bin.zip', '-o', str(gradle)], check=True)
checksum = downloads / 'gradle-8.7-bin.zip.sha256'
if not checksum.exists():
    subprocess.run(['curl', '-fL', '--retry', '3', 'https://services.gradle.org/distributions/gradle-8.7-bin.zip.sha256', '-o', str(checksum)], check=True)
assert hashlib.sha256(gradle.read_bytes()).hexdigest() == checksum.read_text().strip(), 'Gradle checksum mismatch'
if not (tools / 'gradle-8.7/bin/gradle').exists():
    with zipfile.ZipFile(gradle) as archive:
        archive.extractall(tools)
    (tools / 'gradle-8.7/bin/gradle').chmod(0o755)
sdk = pathlib.Path(os.environ['ANDROID_SDK_ROOT'])
cmdtools = downloads / 'commandlinetools-linux-11076708_latest.zip'
if not cmdtools.exists():
    subprocess.run(['curl', '-fL', '--retry', '3', 'https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip', '-o', str(cmdtools)], check=True)
# Official checksum published in Google's repository2-1.xml for command-line tools 12.0.
assert hashlib.sha1(cmdtools.read_bytes()).hexdigest() == 'd313adb7aedccf6cf0cfca51ec180f0059f5f8f8', 'Android tools checksum mismatch'
target = sdk / 'cmdline-tools/12.0'
if not (target / 'bin/sdkmanager').exists():
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(cmdtools) as archive:
        for entry in archive.infolist():
            rel = pathlib.PurePosixPath(entry.filename).relative_to('cmdline-tools')
            path = target.joinpath(*rel.parts)
            if entry.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(entry))
    for path in (target / 'bin').iterdir():
        path.chmod(0o755)
PY
python3 scripts/configure-java-network.py
source "$NOWELL_ANDROID_TOOLS/java-network.env"
sdkmanager --licenses < <(yes)
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" < <(yes)
npm ci --no-audit --no-fund
