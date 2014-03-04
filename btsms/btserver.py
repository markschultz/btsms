import sys, os, struct
from PyOBEX import server
from bluetooth import OBEX_UUID, RFCOMM_UUID, L2CAP_UUID
import bluetooth._bluetooth as _bt
from multiprocessing import Queue

MESSAGE_NOTIFICATION_SERVER_CLASS = '1133'
MESSAGE_ACCESS_PROFILE = '1134', 256


def read_local_bdaddr(hci_sock):
    old_filter = hci_sock.getsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, 14)
    flt = _bt.hci_filter_new()
    opcode = _bt.cmd_opcode_pack(_bt.OGF_INFO_PARAM,
            _bt.OCF_READ_BD_ADDR)
    _bt.hci_filter_set_ptype(flt, _bt.HCI_EVENT_PKT)
    _bt.hci_filter_set_event(flt, _bt.EVT_CMD_COMPLETE);
    _bt.hci_filter_set_opcode(flt, opcode)
    hci_sock.setsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, flt )

    _bt.hci_send_cmd(hci_sock, _bt.OGF_INFO_PARAM, _bt.OCF_READ_BD_ADDR )

    pkt = hci_sock.recv(255)

    status,raw_bdaddr = struct.unpack("xxxxxxB6s", pkt)
    assert status == 0

    t = [ "%X" % ord(b) for b in raw_bdaddr ]
    t.reverse()
    bdaddr = ":".join(t)

    # restore old filter
    hci_sock.setsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, old_filter )
    return bdaddr


class MNS(server.Server):
    def __init__(self, q):
        #server.Server.__init__(self, "00:02:72:DC:21:96")
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
        print("got put")


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
        protocols = [RFCOMM_UUID]
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
        #mns_server.stop_service(socket)


if __name__ == "__main__":
    q = Queue()
    run_server(q)
    sys.exit()
