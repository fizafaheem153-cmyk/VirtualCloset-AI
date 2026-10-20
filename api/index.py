from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>VirtualCloset AI Agent</title></head>
        <body style="font-family: sans-serif; padding: 40px; text-align: center;">
            <h1>👗 VirtualCloset AI — Live Vercel Deployment</h1>
            <p>Agent status: <strong>Active & Ready</strong></p>
            <p>Backend endpoint successfully hosted via Vercel Python Functions.</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
        return
