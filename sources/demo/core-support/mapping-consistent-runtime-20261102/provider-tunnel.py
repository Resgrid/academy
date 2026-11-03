"""Unpublished demo-only CONNECT proxy. TLS stays end-to-end with the provider."""
import select,socket,socketserver
from http.server import BaseHTTPRequestHandler,HTTPServer

ALLOWED={'api.mapbox.com:443','api.weather.gov:443'}
class Handler(BaseHTTPRequestHandler):
 protocol_version='HTTP/1.1'
 def log_message(self,*args):pass  # Never log URLs, tokens, headers or tunnel bytes.
 def do_CONNECT(self):
  if self.path.lower() not in ALLOWED:
   self.send_error(403,'Provider is outside the Academy allowlist');return
  host,port=self.path.rsplit(':',1)
  try:remote=socket.create_connection((host,int(port)),timeout=12)
  except OSError:
   self.send_error(502,'Provider connection unavailable');return
  with remote:
   self.send_response(200,'Connection established');self.end_headers()
   self.connection.settimeout(30);remote.settimeout(30)
   try:
    while True:
     ready,_,_=select.select([self.connection,remote],[],[],30)
     if not ready:return
     for source in ready:
      data=source.recv(65536)
      if not data:return
      (remote if source is self.connection else self.connection).sendall(data)
   except OSError:return
 def do_GET(self):self.send_error(405,'CONNECT only')
class Server(socketserver.ThreadingMixIn,HTTPServer):daemon_threads=True
if __name__=='__main__':Server(('0.0.0.0',3128),Handler).serve_forever()
