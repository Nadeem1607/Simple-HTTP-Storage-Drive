from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
import cgi
import socket

# Define the handler to serve files and handle uploads
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve files directly from the directory where the script is located
        if self.path == '/':
            self.send_response(200)#OK
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Basic HTML for file upload form
            self.wfile.write(b"""
                <html>
                    <body>
                        <h1>Python Drive Project</h1>
                        <form enctype="multipart/form-data" method="post">
                            <input type="file" name="file" />
                            <input type="submit" value="Upload" />
                        </form>
                        <h2>Available Files for Download:</h2>
                        <ul>
            """)

            # List available files for download
            files = os.listdir('.')
            for file in files:
                self.wfile.write(f'<li><a href="{file}">{file}</a></li>'.encode())

            self.wfile.write(b"""
                        </ul>
                    </body>
                </html>
                """)
        else:
            # Serve files from the current directory
            super().do_GET()
    def do_POST(self):
        try:
            # Parse the form data using cgi.FieldStorage
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Extract the uploaded file
            if 'file' in form:
                uploaded_file = form['file']
                filename = os.path.basename(uploaded_file.filename)
                
                # Save the uploaded file
                with open(filename, 'wb') as f:
                    f.write(uploaded_file.file.read())

                # Respond to the client after successful upload
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"""
                    <html>
                        <head>
                            <meta http-equiv="refresh" content="5;url=/" />
                        </head>
                        <body>
                            <h1>File '{filename}' uploaded successfully!</h1>
                            <p>You will be redirected to the upload page in 5 seconds.</p>
                        </body>
                    </html>
                """.encode())
            else:
                self.send_response(400)#HTTP Bad Request
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                        <head>
                            <meta http-equiv="refresh" content="5;url=/" />
                        </head>
                        <body>
                            <h1>No file provided!</h1>
                            <p>You will be redirected to the upload page in 5 seconds.</p>
                        </body>
                    </html>
                """)

        except Exception as e:
            self.send_response(500)#Internal Server Error
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                    <head>
                        <meta http-equiv="refresh" content="5;url=/" />
                    </head>
                    <body>
                        <h1>Error: {str(e)}</h1>
                        <p>You will be redirected to the upload page in 5 seconds.</p>
                    </body>
                </html>
            """.encode())

# Function to get the server's local IP address
def get_local_ip():
    # This method opens a UDP connection to a non-routable address to retrieve the local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to send actual data, just opening the connection
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = '127.0.0.1'  # Fallback to localhost if there's an issue
    finally:
        s.close()
    return ip

# Set up the HTTP server
def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    # Serve from the directory where the Python file is located
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    host = get_local_ip()  # Get the actual IP address of the server
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server on {host}:{port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
