# website tool to configure this application

from twisted.web import resource, server


class HomePage(resource.Resource):

    def __init__(self, r):
        resource.Resource.__init__(self)
        self.r = r

    def render(self, request):
        s = self.r.dumpObs() 
        request.setHeader('Content-Length', len(s))
        request.setHeader('Content-Type', 'text/plain')
        request.setResponseCode(200)
        request.write( s )
        request.finish()
        return server.NOT_DONE_YET


class RootResource(resource.Resource):
    def __init__(self, r):
        resource.Resource.__init__(self)
        self.putChild('', HomePage(r))
