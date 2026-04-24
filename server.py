#!/usr/bin/env python3
"""Sales Playbook server — serves HTML + proxies Zoho CRM API calls."""
import http.server
import json
import os
import socket
import subprocess
import sys

PORT = int(os.environ.get("PORT", 8080))
GRAPH_API_BASE = os.environ.get("GRAPH_API_BASE_URL", "https://graph.trilogycare.com.au")
GRAPH_API_TOKEN = os.environ.get("GRAPH_API_TOKEN", "")
ZOHO_PROXY_ENDPOINT = f"{GRAPH_API_BASE}/services/zoho-actions/v1.0/proxy"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/zoho/notes":
            self._proxy_zoho_note()
        else:
            self.send_error(404)

    def _proxy_zoho_note(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""

        try:
            payload = json.loads(body)
            lead_id = payload.get("lead_id", "")
            note_title = payload.get("note_title", "Sales Call Summary")
            note_content = payload.get("note_content", "")

            zoho_body = json.dumps({
                "data": {
                    "call": {"method": "POST", "version": "v6", "endpoint": "/Notes"},
                    "payload": {
                        "data": [{
                            "Note_Title": note_title,
                            "Note_Content": note_content,
                            "Parent_Id": {
                                "id": lead_id,
                                "module": {"api_name": "Leads"},
                            },
                        }]
                    },
                }
            })

            # Use curl subprocess to avoid urllib SSL/403 issues
            result = subprocess.run(
                [
                    "curl", "-s", "-X", "POST", ZOHO_PROXY_ENDPOINT,
                    "-H", "Content-Type: application/json",
                    "-H", f"Authorization: Bearer {GRAPH_API_TOKEN}",
                    "-d", zoho_body,
                ],
                capture_output=True, text=True, timeout=15,
            )
            response_data = json.loads(result.stdout)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, format, *args):
        sys.stderr.write(f"[playbook] {args[0]}\n")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    srv = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    srv.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(f"Sales Playbook running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
