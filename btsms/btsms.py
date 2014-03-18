#! /usr/bin/python2
import bluetooth
import sqlite3 as sql
from bluetooth import OBEX_UUID, RFCOMM_UUID
import time
import sys
import mytypes
#import client
from multiprocessing import Process, Queue, freeze_support
from PyOBEX import headers, server, responses, client
from xml.dom import minidom


MESSAGE_NOTIFICATION_SERVER_CLASS = '1133'
MESSAGE_ACCESS_PROFILE = '1134', 256


class MNS(server.Server):
    def __init__(self, q):
        server.Server.__init__(self, "")
        self.q = q

    def sendall(self, socket, data):
        while data:
            ret = socket.send(data)
            assert ret > 0
            data = data[ret:]

    def send_response(self, socket, response, header_list=[]):

        while header_list:

            if response.add_header(header_list[0], self._max_length()):
                header_list.pop(0)
            else:
                self.sendall(socket, response.encode())
                response.reset_headers()

        # Always send at least one request.
        self.sendall(socket, response.encode())

    def put(self, socket, request):
        body = ""
        while True:
            for header in request.header_data:
                if isinstance(header, headers.Body):
                    body += header.decode()
                elif isinstance(header, headers.End_Of_Body):
                    body += header.decode()
            if request.is_final():
                break
            self.send_response(socket, responses.Continue())
            request = self.request_handler.decode(socket)
        self.q.put(body)
        self.send_response(socket, responses.Success())

def run_server(q):
    try:
        mns_server = MNS(q)
        port = 0
        name = "MNS"
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
        print("begin serving")
        mns_server.serve(socket)
        print("serving started")
    except IOError:
        print(sys.exc_info())
        mns_server.stop_service(socket)


def GetMessage(c, handle):
    resp = c.get(name=handle, header_list=[headers.Type('x-by/message'), headers.App_Parameters('\x14\x01\x01')])
    return resp

def GetMessageListing(c, params):
    resp = c.get(name="inbox", header_list=[headers.Type("x-bt/MAP-msg-listing"),
    headers.App_Parameters(params)])
    #headers.App_Parameters('\x10\x04\x00\x00\x10\x6b\x13\x01\xff')])
    return resp

def PushMessage(c, t, f, body):
    resp = c.put(name="outbox", file_data=msg,
                 header_list=[headers.Type("x-bt/message"),
                              headers.App_Parameters('\x14\x01\x01')])
    return resp


def SetNotificationRegistration(c, connect):
    happ = headers.App_Parameters('\x0e\x01' + ('\x01' if connect else '\x00'))
    c.put(name="", file_data='\x30',
          header_list=[
              headers.Type("x-bt/MAP-NotificationRegistration"), happ])
    print ("Notification Registration:" + str(connect))

if __name__ == '__main__':
    freeze_support()
    q = Queue()
    p = Process(target=run_server, args=(q,))
    p.daemon
    #p.start()
    #con = sql.connect("btsms.db")
    #c = con.cursor()
    #c.execute('SELECT SQLITE_VERSION()')
    #print(c.fetchone())
    #sys.exit()
    #devices = bluetooth.discover_devices()
    devices = ""
    address = "30:19:66:bc:8e:94"
    for d in devices:
        print ("device name: " + bluetooth.lookup_name(d) + " @ " + d)
        if bluetooth.lookup_name(d) == "SM-N900V":
            address = d

    #services = bluetooth.find_service(address=address)
    services = ""

    print ("found services: ")
    for s in services:
        if s['name'] is None:
            continue
        print ("name: {0}, port: {1}, profiles: {2}".format(
            s['name'], s['port'], s['profiles']))

    map = bluetooth.find_service(uuid="1134", address=address)[0]
    #print(map)
    port = map['port']
    c = client.Client(address, port)
    h = headers.Target(
        '\xBB\x58\x2B\x40\x42\x0C\x11\xDB\xB0\xDE\x08\x00\x20\x0C\x9A\x66')
    conn = c.connect(header_list=[h])
    print ("connected")
    resp = c.setpath(name="telecom")
    resp = c.setpath(name="msg")
    #PushMessage(c, "3124361855", "8477722763", "this is the body of the message")
    GetMessageListing(c, '')
    SetNotificationRegistration(c, True)
    r = q.get()
    mer = mytypes.xmlToMapEventReport(r)
    print(mer)
    SetNotificationRegistration(c, False)
    c.disconnect()
    print ("disconnected, exiting")