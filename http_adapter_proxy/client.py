from typing import Tuple, Union, Optional
import socket
from requests.adapters import BaseAdapter
from requests import adapters, Response, PreparedRequest, sessions
from .proto import sendobjs, recvobjs

HTTPAdapter = adapters.HTTPAdapter()


class ProxyAdapter(BaseAdapter):
    """HTTPAdapter for :module:`requests` to use the proxy"""

    def __init__(self, socket_filename, proxy_timeout: Optional[float] = None):
        super().__init__()
        self.socket_filename = socket_filename
        self.proxy_timeout = proxy_timeout

    def close(self) -> None:
        pass

    def send(self,
             request: PreparedRequest,
             stream: bool = None,
             timeout: Union[None, float, Tuple[float, float]] = None,
             verify: bool = True,
             cert=None,
             proxies=None) -> Response:
        conn = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        if self.proxy_timeout:
            conn.settimeout(self.proxy_timeout)
        conn.connect(self.socket_filename)
        sendobjs(conn, request, stream, timeout, verify, cert, proxies)
        ret = recvobjs(conn)
        conn.close()
        if isinstance(ret[0], Response):
            return ret[0]
        else:
            raise ret[0]


def patch_http_adapter(socket_filename, proxy_timeout: Optional[float] = None):
    """patch the :module:`requests` module to use ProxyAdapter by default"""
    class HTTPAdapter(ProxyAdapter):
        def __init__(self):
            super().__init__(socket_filename, proxy_timeout)

        def close(self):
            pass

    adapters.HTTPAdapter = HTTPAdapter
    sessions.HTTPAdapter = HTTPAdapter
