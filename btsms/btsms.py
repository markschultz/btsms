#! /usr/bin/python2
import bluetooth
import btserver
from multiprocessing import Process, Queue
from PyOBEX import client, headers


def SetNotificationRegistration(c, connect):
    happ = headers.App_Parameters('\x0e\x01' + ('\x01' if connect else '\x00'))
    c.put(name="", file_data='\x30',
          header_list=[
              headers.Type("x-bt/MAP-NotificationRegistration"), happ])
    print ("Notification Registration:" + str(connect))

devices = bluetooth.discover_devices()
address = ""
for d in devices:
    print ("device name: " + bluetooth.lookup_name(d) + " @ " + d)
    if bluetooth.lookup_name(d) == "SM-N900V":
        address = d

services = bluetooth.find_service(address=address)

print ("found services: ")
for s in services:
    if s['name'] is None:
        continue
    print ("name: {0}, port: {1}, profiles: {2}".format(
        s['name'], s['port'], s['profiles']))

map = bluetooth.find_service(uuid="1134", address=address)[0]
#map = bluetooth.find_service(uuid = "1105", address = address)[0]
port = map['port']
print ("connecting to map")
c = client.Client(address, port)
h = headers.Target(
    '\xBB\x58\x2B\x40\x42\x0C\x11\xDB\xB0\xDE\x08\x00\x20\x0C\x9A\x66')
conn = c.connect(header_list=[h])
print ("connected")
resp = c.setpath(name="telecom")
resp = c.setpath(name="msg")
#resp = c.get(name="inbox", header_list=[headers.Type("x-bt/MAP-msg-listing"),
#headers.App_Parameters('\x01\x02\x00\x02\x10\x04\x00\x00\x96\x8f')])
#resp = c.get(name="0100000000000001", header_list=
#[headers.Type("x-bt/message"), headers.App_Parameters('\x14\x01\x01')])
msg = "BEGIN:BMSG\r\nVERSION:1.0\r\nSTATUS:READ\r\nTYPE:SMS_CDMA\r\nFOLDER:telecom/msg/outbox\r\nBEGIN:VCARD\r\nVERSION:2.1\r\nFN:Mark Schultz\r\nTEL:8477722763\r\nEND:VCARD\r\nBEGIN:BENV\r\nBEGIN:VCARD\r\nVERSION:2.1\r\nFN:GrandCentral\r\nTEL:3124361855\r\nEND:VCARD\r\nBEGIN:BBODY\r\nCHARSET:UTF-8\r\nLENGTH:{1}\r\nBEGIN:MSG\r\n{0}\r\nEND:MSG\r\nEND:BBODY\r\nEND:BENV\r\nEND:BMSG\r\n"
body = "test message"
msg = msg.format(body, len(body))
resp = c.put(name="outbox", file_data=msg,
             header_list=[headers.Type("x-bt/message"),
                          headers.App_Parameters('\x14\x01\x01')])
q = Queue()
p = Process(target=btserver.run_server, args=(q,))
p.start()
SetNotificationRegistration(c, True)
while True:
    print (q.get())
p.join()
c.disconnect()
print ("disconnected, exiting")
