from urllib.parse import urlparse, urlunparse

from twisted.web.http import HTTPFactory
from twisted.web.proxy import Proxy, ProxyRequest

__all__ = (
    'CachingProxy',
    'CachingProxyFactory',
    'CachingProxyRequest',
)


class CachingProxyRequest(ProxyRequest):
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

        super().process()


class CachingProxy(Proxy):
    requestFactory = CachingProxyRequest


class CachingProxyFactory(HTTPFactory):
    def buildProtocol(self, address):
        return CachingProxy()
