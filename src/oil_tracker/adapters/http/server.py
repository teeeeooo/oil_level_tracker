from __future__ import annotations

import socketserver
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    # The page loads its JavaScript modules over many connections at once. The default queue of 5
    # reset some of them, and a page missing one module stays blank.
    request_queue_size = 64

    def server_bind(self) -> None:
        # HTTPServer.server_bind calls socket.getfqdn(), a reverse DNS lookup that can
        # stall for tens of seconds on some networks; a 127.0.0.1 server never needs it.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]


def start_server(handler: type[BaseHTTPRequestHandler], port: int = 0) -> LocalServer:
    server = LocalServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, name="http", daemon=True).start()
    return server
