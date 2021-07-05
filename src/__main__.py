from os import getenv

from twisted.internet import reactor

from proxy import CachingProxyFactory

# just type hinting for PyCharm
from twisted.internet.posixbase import PosixReactorBase

# noinspection PyTypeChecker
reactor = reactor  # type: PosixReactorBase

reactor.listenTCP(getenv('PORT', 8080), CachingProxyFactory())
print('Listening on port 8080…')
reactor.run()
