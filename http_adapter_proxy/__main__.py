from sys import argv
from .server import ProxyServer
import logging


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    domains = {}
    if len(argv) > 3:
        for domain, num in zip(argv[2::2], argv[3::2]):
            domains[domain] = int(num)
    ProxyServer(socket_path=argv[1], domains=domains).listen()
