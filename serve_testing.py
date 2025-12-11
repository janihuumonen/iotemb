from http.server import HTTPServer, BaseHTTPRequestHandler

ip = '185.96.163.69'
port = 8080
n = 0

class Serv(BaseHTTPRequestHandler):

   def do_GET(self):
      global n
      if self.path == '/':
          self.path = '/test.html'
      try:
          file_to_open = f'hello {n}'
          n += 1
          self.send_response(200)
      except:
          file_to_open = "File not found"
          self.send_response(404)
      self.end_headers()
      self.wfile.write(bytes(file_to_open, 'utf-8'))

   def do_POST(self):
      content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
      post_data = self.rfile.read(content_length) # <--- Gets the data itself
      #logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
      #        str(self.path), str(self.headers), post_data.decode('utf-8'))
      print(post_data.decode('utf-8'))

      self.send_response(200)
      self.end_headers()
      self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


httpd = HTTPServer((ip,port),Serv)
httpd.serve_forever()

