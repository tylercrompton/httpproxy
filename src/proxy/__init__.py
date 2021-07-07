import pymongo
from hashlib import sha256
from urllib.parse import urlparse, urlunparse

from twisted.web.http import HTTPFactory
from twisted.web.proxy import Proxy, ProxyClient, ProxyClientFactory, ProxyRequest

from cache import collection
from cache.drivers import MongoDBCacheDriver

__all__ = (
    'CachingProxy',
    'CachingProxyClient',
    'CachingProxyClientFactory',
    'CachingProxyFactory',
    'CachingProxyRequest',
)


class CachingProxyClient(ProxyClient):
    def handleResponseEnd(self):
        super().handleResponseEnd()
        pass


class CachingProxyClientFactory(ProxyClientFactory):
    protocol = CachingProxyClient


class CachingProxyRequest(ProxyRequest):
    protocols = {b'http': CachingProxyClientFactory}

    # `twisted.web.http.Request.requestReceived` is bugged. It expects the
    # `path` parameter to be a URI, but it's actually just the path component of
    # the URI. `twisted.web.proxy.ProxyRequest.process` incorrectly assumes that
    # `self.uri` is a URI. With insufficient time to open a ticket with Twisted
    # and have the issue formally resolved and released, we're just going to
    # monkey patch `self.uri` to actually be a URI and hope for the best.
    def process(self):
        parsed = urlparse(self.uri)

        # Assume HTTP for now.
        scheme = b'http'
        # Assume port 80 for now.
        netloc = b':'.join([
            self.getRequestHostname(),
            b'80',
        ])

        self.uri = urlunparse((scheme, netloc, *parsed[2:]))

        parsed = urlparse(self.uri)
        protocol = parsed[0]
        host = parsed[1].decode("ascii")
        port = self.ports[protocol]
        if ":" in host:
            host, port = host.split(":")
            port = int(port)
        rest = urlunparse((b"", b"") + parsed[2:])
        if not rest:
            rest = rest + b"/"
        class_ = self.protocols[protocol]
        headers = self.getAllHeaders().copy()
        if b"host" not in headers:
            headers[b"host"] = host.encode("ascii")
        self.content.seek(0, 0)
        s = self.content.read()
        clientFactory = class_(self.method, rest, self.clientproto, headers, s, self)
        self.reactor.connectTCP(host, port, clientFactory)


class CachingProxyFactory(HTTPFactory):
    _driver = MongoDBCacheDriver(collection)

    def buildProtocol(self, address):
        return CachingProxy()

    def log(self, request=None):
        super().log(request)

        uri_digest = sha256(self.uri).hexdigest()

        # Cache response here.
        self._driver.cache_response(
            self.uri,
            None,
            self.content.getvalue(),
        )
        # with open(f'data/{uri_digest}', 'bw') as cached_response_file:
        #     cached_response_file.write(self.content.getvalue())


class CachingProxy(Proxy):
    factory = CachingProxyFactory
    requestFactory = CachingProxyRequest
