import re
from xml.dom import minidom

class MapMsgListing:
    def __init__(self, listing):
        self.listing = listing

class BtMessage:
    def __init__(self, t, f, body, len, type, status):
        self.t = t
        self.f = f
        self.body = body
        self.len = len
        self.type = type
        self.status = status

class MapEventReport:
    def __init__(self, type, handle="0", folder="telecom/msg/inbox", old_folder="", msg_type=""):
        self.type = type
        self.handle = handle
        self.folder = folder
        self.old_folder = old_folder
        self.msg_type = msg_type

def xmlToMapEventReport(xmlstring):
    xmldoc = minidom.parseString(xmlstring)
    itemList = xmldoc.getElementsByTagName('event')
    MERList = []
    for s in itemList:
        attrs = {'type': None, 'handle': None, 'folder': None, 'old_folder': None, 'msg_type': None}
        for key in attrs:
            try:
                attrs[key] = s.attributes[key].value
            except:
                attrs[key] = None
        MERList.append(MapEventReport(type=attrs['type'], handle=attrs['handle'], folder=attrs['folder'], old_folder=attrs['old_folder'], msg_type=attrs['msg_type']))
    return MERList

def XmlToBtMessage(xmlstring):
    r = re.search('(?<=TYPE:)\w+', xmlstring)
    type = r.group(0)
    r = re.search('(?<=STATUS:)\w+', xmlstring)
    status = r.group(0)
    r = re.search('(?<=LENGTH:)\w+', xmlstring)
    len = r.group(0)
    r = re.search('(?<=BEGIN:MSG)(.*\w+)(?=END:MSG)', xmlstring, re.DOTALL)
    body = r.group(0).strip("\r\n")
    r = re.search('(?<=TEL:)\w+', xmlstring)
    t = r.group(1)
    f = r.group(0)
    return BtMessage(t, f, body, len, type, status)

def BtMessageToXml(btmsg):
    xmlstring = "BEGIN:BMSG\r\nVERSION:1.0\r\nSTATUS:READ\r\nTYPE:{4}\r\nFOLDER:telecom/msg/outbox\r\nBEGIN:VCARD\r\nVERSION:2.1\r\nTEL:{3}\r\nEND:VCARD\r\nBEGIN:BENV\r\nBEGIN:VCARD\r\nVERSION:2.1\r\nTEL:{2}\r\nEND:VCARD\r\nBEGIN:BBODY\r\nCHARSET:UTF-8\r\nLENGTH:{1}\r\nBEGIN:MSG\r\n{0}\r\nEND:MSG\r\nEND:BBODY\r\nEND:BENV\r\nEND:BMSG\r\n"
    xmlstring = xmlstring.format(btmsg.body, btmsg.len, btmsg.t, btmsg.f, btmsg.type)
    return xmlstring

def MapMsgListingToBtMessages(xmlstring):
    return ""