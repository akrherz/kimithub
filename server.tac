
from twisted.application import service, internet
from twisted.cred import checkers, portal
from twisted.web import server as webserver

from nwnserver import server, auth
from nwnserver.scripts import rainwise
from nwnserver import filewatcher

import receiver

# Hack around 2.0 problem
from twisted.internet import reactor, base
reactor.installResolver(base.BlockingResolver())


userPassFile = "./passwords.txt"
remoteServerIP = 'mesonet.agron.iastate.edu'
remoteServerPort = 14996
remoteServerUser = '...'
remoteServerPass = '...'

myPortal = portal.Portal(auth.NWNRealm())
myPortal.registerChecker(checkers.FilePasswordDB(userPassFile))

application = service.Application("KIMT NWN Server")
serviceCollection = service.IServiceCollection(application)

nwn_factory = server.NWNServerFactory(myPortal)
rw_factory = server.NWNServerFactory(myPortal)

r = receiver.ReceiverFactory(nwn_factory, rw_factory)

# Connect to NWN Hub, to get KCCI's sites for KIMT to use
rapp = internet.TCPClient(remoteServerIP, remoteServerPort, rainwise.MyClientFactory(remoteServerUser, remoteServerPass, rw_factory))
rapp.setServiceParent(serviceCollection)

# Listen for Folks that want data in RW format
rw_localServerPort = 15001
rwapp = internet.TCPServer(rw_localServerPort, rw_factory)
rwapp.setServiceParent(serviceCollection)

# Listen for folks that want data in NWN format
nwn_localServerPort = 15002
nwnapp = internet.TCPServer(nwn_localServerPort, nwn_factory)
nwnapp.setServiceParent(serviceCollection)

# Listen for machines out there willing to share data!
receiverPort = 15000
r2app = internet.TCPServer(receiverPort, r)
r2app.setServiceParent(serviceCollection)


# Setup HTTP config interface
import website
webport = 8000
w = webserver.Site(website.RootResource(r))
web = internet.TCPServer(webport, w)
web.setServiceParent(serviceCollection)
