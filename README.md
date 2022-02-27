# py-http-adapter-proxy

Used to put http/https requests (sent by [python requests module](https://github.com/psf/requests) in **localhost**) from different processes into queues, with HTTP keep-alive enabled.

The program have the client (can be more than one, e.g. multiple processes) and server part, and they communicate via (and only via) unix socket. The proxy protocol is dependent on [pickle](https://docs.python.org/3/library/pickle.html), which is **not secure**, so the client is restricted to the ones in localhost with permission to access the unix socket file created by server-side.

## Why py-http-adapter-proxy

The program was written for reuse the http connections (HTTP keep-alive) as many as possible even if http requests are sent in different processes.

## Run

### Server-side

Run in shell:

```bash
python3 -m http_adapter_proxy PATH_TO_SOCKET_FILE [PROTOCOL://DOMAIN QUEUE_SIZE] ...
```

or run in python:

```python
from http_adapter_proxy.server import ProxyServer
domains = { # optional
	"http://google.com": 32, # size of the queue of requests to the protocol://domain
	"http://www.baidu.com": 8
}
# other=16: a queue with 16 as size will be created for all protocol://domain not in domains dict
ProxyServer(socket_path="path_to_socket_file.sock", domains=domains, other=16).listen()
```

### Client-side

Use `http_adapter_proxy.client.ProxyAdapter` provided as the compatible class:

```python
from http_adapter_proxy.client import ProxyAdapter
from requests import Session
adapter = ProxyAdapter("path_to_socket_file.sock")
s = Session()
s.mount("http://", adapter)
s.mount("https://", adapter)
s.get("http://google.com")
```

or use `http_adapter_proxy.client.patch_http_adapter` which set the default HTTPAdapter of `requests` module to `ProxyAdapter`:

```python
from http_adapter_proxy.client import patch_http_adapter
import requests
patch_http_adapter("path_to_socket_file.sock")
requests.get("http://google.com")
s = requests.Session()
s.get("http://google.com")
```

# TODO

- safe
- support for `max_retries` arguments of [HTTPAdapter](https://docs.python-requests.org/en/latest/api/#requests.adapters.HTTPAdapter)
- document
- cancel (in server-side) the requests canceled in client

# License

AGPLv3.0
