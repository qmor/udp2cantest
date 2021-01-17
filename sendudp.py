import socket
import pickle
import can
from optparse import OptionParser

parser = OptionParser(usage="usage: %prog [options]\n")
parser.add_option("-d", "--host", dest="host", default="127.0.0.1", help="address to send message to")
parser.add_option("-p", "--port", dest="port", default=9000, help="port to send message to")
parser.add_option("-a", "--arguments", dest="args", default="", help="can packet data arguments")
parser.add_option("-i", "--id", dest="canid", default="0")

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
(options, args) = parser.parse_args()
_args = options.args.split(",")
args = []
canid = int(options.canid, 16) if options.canid.lower().find('0x') != -1 else int(options.canid)
for i in _args:
    if i != "":
        if i.lower().find("0x") != -1:
            args.append(int(i, 16))
        else:
            args.append(int(i, 10))

msg = can.message.Message(arbitration_id=canid, data=args)
msgpickle = pickle.dumps(msg)

socket.sendto(msgpickle, (options.host, int(options.port)))
