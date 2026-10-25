#!/usr/bin/env python3
"""Use the environment's proxy and supplied CA without weakening TLS checks."""
import hashlib
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import urllib.parse

tools = pathlib.Path(os.environ["NOWELL_ANDROID_TOOLS"])
jdk = pathlib.Path(os.environ["JAVA_HOME"])
properties = {}
sdk_options = []
proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
if proxy:
    parsed = urllib.parse.urlsplit(proxy)
    if parsed.username or parsed.password:
        raise SystemExit("Proxy authentication must be provided by the environment, not copied into build files")
    for protocol in ("http", "https"):
        properties[f"systemProp.{protocol}.proxyHost"] = parsed.hostname
        properties[f"systemProp.{protocol}.proxyPort"] = str(parsed.port or 8080)
        sdk_options.extend([f"-D{protocol}.proxyHost={parsed.hostname}", f"-D{protocol}.proxyPort={parsed.port or 8080}"])
    properties["systemProp.http.nonProxyHosts"] = "localhost|127.*|[::1]"

cert_source = os.environ.get("NODE_EXTRA_CA_CERTS") or os.environ.get("CODEX_PROXY_CERT")
if cert_source and pathlib.Path(cert_source).is_file():
    truststore = tools / "java-truststore"
    if not truststore.exists():
        shutil.copy2(jdk / "lib/security/cacerts", truststore)
    for pem in re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", pathlib.Path(cert_source).read_text(), re.S):
        fingerprint = hashlib.sha256(pem.encode()).hexdigest()
        alias = "nowell-env-" + fingerprint
        cert_file = tools / (alias + ".pem")
        cert_file.write_text(pem + "\n")
        command = [str(jdk / "bin/keytool"), "-keystore", str(truststore), "-storepass", "changeit", "-alias", alias]
        exists = subprocess.run(command + ["-list"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not exists:
            subprocess.run(command + ["-importcert", "-noprompt", "-trustcacerts", "-file", str(cert_file)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    properties["systemProp.javax.net.ssl.trustStore"] = str(truststore)
    properties["systemProp.javax.net.ssl.trustStorePassword"] = "changeit"
    sdk_options.extend([f"-Djavax.net.ssl.trustStore={truststore}", "-Djavax.net.ssl.trustStorePassword=changeit"])

gradle_dir = pathlib.Path(os.environ["GRADLE_USER_HOME"])
gradle_dir.mkdir(parents=True, exist_ok=True)
path = gradle_dir / "gradle.properties"
lines = path.read_text().splitlines() if path.exists() else []
lines = [line for line in lines if line.partition("=")[0] not in properties]
lines.extend(key + "=" + value for key, value in properties.items())
path.write_text("\n".join(lines) + "\n")
(tools / "java-network.env").write_text("export SDKMANAGER_OPTS=" + shlex.quote(" ".join(sdk_options)) + "\n")
print("Configured Java proxy and environment CA; certificate verification remains enabled")
