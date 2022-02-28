from typing import Dict, Optional
from queue import LifoQueue
from os import unlink, path
import socket
from logging import info, warning
from gevent import spawn, monkey
from .proto import recvobjs, sendobjs
monkey.patch_all()

from requests.adapters import HTTPAdapter
from .serialize import deserialize_requests_prepared_request, serialize_requests_response


class ProxyServer():
    """Server"""

    def _handler(self, conn: socket.socket):
        info("Connected with client")
        if self.proxy_timeout:
            conn.settimeout(self.proxy_timeout)
        try:
            args = recvobjs(conn)
            req = deserialize_requests_prepared_request(args[0])
            info("Url: %s", req.url)
            domain = '/'.join(req.url.split('/', maxsplit=4)[:3])
        except Exception as except_:  # pylint: disable=broad-except
            warning("Catch exception when receiving data: %s", except_)
            conn.close()
            return
        queue = self.adapters.get(domain) or self.adapters.get("*")
        info("Domain: %s, HTTPAdapters: %d", domain, queue.qsize())
        adapter = queue.get()
        try:
            resp = adapter.send(
                req,
                *args[1:]
            )
        except Exception as except_:  # pylint: disable=broad-except
            try:
                sendobjs(conn, except_)
            except Exception as except_:  # pylint: disable=broad-except
                warning(
                    "Fail to send the exception thrown by requests: %s",
                    except_
                )
        else:
            try:
                sendobjs(conn, serialize_requests_response(resp))
            except Exception as except_:  # pylint: disable=broad-except
                warning("Fail to send requests.Response: %s", except_)
        finally:
            queue.put(adapter)
        conn.close()

    def listen(self):
        """listen"""
        sock = socket.socket(family=socket.AF_UNIX,
                             type=socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if path.exists(self.socket_path):
            unlink(self.socket_path)
        sock.bind(self.socket_path)
        sock.listen()
        while True:
            conn, _ = sock.accept()
            spawn(self._handler, conn)

    def __init__(self, socket_path,
                 proxy_timeout: float = 10,
                 domains: Optional[Dict[str, int]] = None,
                 other: int = 16):
        self.adapters: Dict[str, LifoQueue[HTTPAdapter]] = {
            domain: LifoQueue(maxsize=num) for domain, num in (domains or {}).items()
        }
        self.adapters["*"] = LifoQueue(maxsize=other)
        for queue in self.adapters.values():
            for _ in range(queue.maxsize):
                queue.put(HTTPAdapter())
        self.socket_path = socket_path
        self.proxy_timeout = proxy_timeout
