import http.server
import socketserver
import cgi
import os
import subprocess
import json

PORT = 8080

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/generate':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type'],
                         }
            )
            
            # Check if file is uploaded
            if 'image' not in form:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No image uploaded")
                return
                
            fileitem = form['image']
            if not fileitem.file:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No file content")
                return
                
            filename = os.path.basename(fileitem.filename)
            upload_path = os.path.join(os.getcwd(), filename)
            
            # Save uploaded file
            with open(upload_path, 'wb') as f:
                f.write(fileitem.file.read())
            
            # Get options
            grid = form.getvalue('grid', '32')
            colors = form.getvalue('colors', '20')
            art_id = form.getvalue('id', '')
            title = form.getvalue('title', '')
            category = form.getvalue('category', 'popular')
            preview = form.getvalue('preview', 'img_home1')
            output = form.getvalue('output', 'artworks.json')
            append = form.getvalue('append', 'false')
            
            # Construct command
            cmd = ["python3", "png_to_artwork.py", filename, "--grid", grid, "--colors", colors, "--category", category, "--preview", preview, "--output", output, "--preview-png"]
            if art_id: cmd.extend(["--id", art_id])
            if title: cmd.extend(["--title", title])
            if append == 'true': cmd.append("--append")
            
            # Run command
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": e.stderr + "\n" + e.stdout}).encode())
                return
                
            # The preview image is saved as filename_preview.png
            preview_png_name = os.path.splitext(filename)[0] + "_preview.png"
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "success": True,
                "preview_url": f"/{preview_png_name}",
                "json_url": f"/{output}",
                "logs": result.stdout
            }
            self.wfile.write(json.dumps(response).encode())

# Lấy thư mục chứa file server.py và chuyển thư mục làm việc về đó
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"🚀 Server running at http://localhost:{PORT}/web_ui/index.html")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    httpd.serve_forever()
