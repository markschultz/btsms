from xml.dom import minidom


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