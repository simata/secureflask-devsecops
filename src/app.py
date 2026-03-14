import subprocess
import logging

from flask import Flask, request, jsonify
from src.config import Config

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Sample vulnerability data (mock database) ---
VULN_DATABASE = {
    "CVE-2024-1234": {
        "severity": "HIGH",
        "package": "openssl",
        "description": "Buffer overflow in TLS handshake",
        "cvss": 8.1,
    },
    "CVE-2024-5678": {
        "severity": "CRITICAL",
        "package": "log4j",
        "description": "Remote code execution via JNDI lookup",
        "cvss": 10.0,
    },
    "CVE-2024-9999": {
        "severity": "MEDIUM",
        "package": "requests",
        "description": "SSRF via crafted redirect",
        "cvss": 5.3,
    },
}


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "secureflask"})


@app.route("/api/v1/vulns", methods=["GET"])
def list_vulnerabilities():
    """List all known vulnerabilities."""
    severity = request.args.get("severity")
    results = VULN_DATABASE

    if severity:
        results = {
            cve_id: details
            for cve_id, details in VULN_DATABASE.items()
            if details["severity"].upper() == severity.upper()
        }

    return jsonify({"count": len(results), "vulnerabilities": results})


@app.route("/api/v1/vulns/<cve_id>", methods=["GET"])
def get_vulnerability(cve_id):
    """Look up a specific CVE."""
    vuln = VULN_DATABASE.get(cve_id.upper())
    if not vuln:
        return jsonify({"error": "CVE not found"}), 404
    return jsonify({"cve_id": cve_id.upper(), **vuln})


# ---------------------------------------------------------------
# INTENTIONALLY INSECURE ENDPOINTS (for Bandit / SAST to catch)
# These exist so you can see what security scanning flags.
# In a real project, you would fix these before merging.
# ---------------------------------------------------------------


@app.route("/api/v1/lookup", methods=["POST"])
def dns_lookup():
    """
    INSECURE: Uses subprocess with shell=True.
    Bandit will flag this as B602 (subprocess_popen_with_shell_equals_true).
    """
    data = request.get_json()
    hostname = data.get("hostname", "")
    # INSECURE — shell=True with user input is command injection risk
    result = subprocess.run(
        f"nslookup {hostname}", shell=True, capture_output=True, text=True
    )
    return jsonify({"output": result.stdout})


@app.route("/api/v1/debug", methods=["GET"])
def debug_info():
    """
    INSECURE: Exposes application secrets in response.
    Bandit will flag the hardcoded password as B105.
    """
    password = "SuperSecret123!"  # nosec — intentional for demo
    return jsonify(
        {
            "debug": True,
            "secret_key": app.config["SECRET_KEY"],
            "db_url": app.config["DATABASE_URL"],
        }
    )


if __name__ == "__main__":
    # INSECURE: binding to 0.0.0.0 with debug=True
    # Bandit flags B104 (binding to all interfaces)
    app.run(host="0.0.0.0", debug=True, port=5000)