import os, struct, sys
from PyOBEX import headers, requests, responses, server
import bluetooth
from bluetooth import OBEX_UUID, RFCOMM_UUID
from multiprocessing import Queue

MESSAGE_NOTIFICATION_SERVER_CLASS = '1133'
MESSAGE_ACCESS_PROFILE = '1134', 256
class MNS(server.Server):
    def __init__(self, q):
        server.Server.__init__(self)
        self.q = q

    def put(self, socket, request):
        q.put("put operation")

def run_server(q):
    try:
        mns_server = MNS(q)
        #def start_service(self, port, name, uuid, service_classes, service_profiles, provider, description, protocols):
        port = 0
        name = "MNS"
        #uuid = '\xbb\x58\x2b\x41\x42\x0c\x11\xdb\xb0\xde\x08\x00\x20\x0c\x9a\x66'
        uuid = 'bb582b41-420c-11db-b0de-0800200c9a66'
        service_classes = [MESSAGE_NOTIFICATION_SERVER_CLASS]
        service_profiles = [MESSAGE_ACCESS_PROFILE]
        provider = ""
        description = "Message Notification Server for MAP Profile"
        protocols = [RFCOMM_UUID, OBEX_UUID]
        socket = mns_server.start_service(port,
                                          name,
                                          uuid,
                                          service_classes,
                                          service_profiles,
                                          provider,
                                          description,
                                          protocols)
        mns_server.serve(socket)
    except IOError:
        mns_server.stop_service(socket)


if __name__ == "__main__":
    q = Queue()
    run_server(q)
    sys.exit()
