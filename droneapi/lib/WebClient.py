from webapi_pb2 import *
import sys
import socket
import time
import logging
import uuid
import threading

logger = logging.getLogger(__name__)

def delimitProtobuf(src):
    """Python protobuf bindings are missing writeDelimited, this is a workaround to add a delimiter"""
    from google.protobuf.internal import encoder

    serializedMessage = src.SerializeToString()
    delimiter = encoder._VarintBytes(len(serializedMessage))

    return delimiter + serializedMessage

def readDelimited(sock):
    """Read a delmited protobuf from a socket"""
    # FIXME - current implementation is very expensive in terms of heap thrash and it will fail for protobufs bigger than  32768 bytes
    from google.protobuf.internal import decoder
    delimsize = 2
    delimbytes = sock.recv(delimsize)
    (payloadsize, pos) = decoder._DecodeVarint(delimbytes, 0)
    # We now know size of our msg, but we might have unused bytes from the delimeter
    numextra = delimsize - pos
    numtoread = payloadsize - numextra
    payload = delimbytes[pos:] + sock.recv(numtoread, socket.MSG_WAITALL)
    msg = Envelope()
    #print "payloadsize=%d, pos=%d, numextra=%d, numtoread=%d, paylen=%d" % (payloadsize, pos, numextra, numtoread, len(payload))
    msg.ParseFromString(payload)
    return msg

class GCSHooks(object):
    def __init__(self, host = "api.3drobotics.com", port = 5555):
        connecttimeout = 15
        readtimeout = 30
        self.sock = socket.create_connection((host, port), connecttimeout)
        self.sock.settimeout(60 * 60)
        self.sock.setblocking(True)
        self.startTime = long(round(time.time() * 1e6)) # time in usecs since 1970

    def filterMavlink(self, fromInterface, bytes):
        #logger.debug("filter mavlink")
        curtime = long(round(time.time() * 1e6))

        e = Envelope()
        l = e.mavlink
        l.srcInterface = fromInterface
        l.packet.append(bytes)
        l.deltaT = curtime - self.startTime
        self.send(e)
        pass

    def loginUser(self, userName, password):
        logger.debug("login user")
        e = Envelope()
        l = e.login
        l.code = LOGIN
        l.username = userName
        l.password = password
        l.startTime = self.startTime
        self.send(e)
        self.__checkLoginOkay()

    def isUsernameAvailable(self, userName):
        logger.debug("is username available")
        e = Envelope()
        l = e.login
        l.code = CHECK_USERNAME
        l.username = userName
        self.send(e)
        r = self.__readLoginResponse()
        return r.code == LoginResponseMsg.OK

    def createUser(self, userName, password, email = None):
        logger.debug("create user")
        e = Envelope()
        l = e.login
        l.code = CREATE
        l.username = userName
        l.password = password
        if not email is None:
            l.email = email
        l.startTime = self.startTime
        self.send(e)
        self.__checkLoginOkay()

    def send(self, envelope):
        #logger.debug("send " + str(envelope))
        self.sock.send(delimitProtobuf(envelope))

    def startMission(self, keep, uuid):
        logger.debug("start mission")
        e = Envelope()
        l = e.startMission
        l.keep = keep
        l.uuid = str(uuid)
        self.send(e)

    def stopMission(self, keep):
        logger.debug("stop mission")
        e = Envelope()
        l = e.stopMission
        l.keep = keep
        self.send(e)

    def setVehicleId(self, vehicleId, fromInterface, mavlinkSysId, allowControl, wantPipe = False):
        logger.debug("set vehicleid")
        e = Envelope()
        l = e.setSender
        l.gcsInterface = fromInterface
        l.sysId = mavlinkSysId
        l.vehicleUUID = str(vehicleId)
        l.canAcceptCommands = allowControl
        l.wantPipe = wantPipe
        self.send(e)

    def flush(self):
        # FIXME - add this (and turn off nagel algorithm and blocking)
        pass

    def close(self):
        self.sock.close()

    def readEnvelope(self):
        return readDelimited(self.sock)

    def __readLoginResponse(self):
        self.flush() # Make sure all previous commands are sent
        r = self.readEnvelope().loginResponse
        if r.code == LoginResponseMsg.CALL_LATER:
            raise Exception('Callback later')
        return r

    def __checkLoginOkay(self):
        r = self.__readLoginResponse()
        if r.code != LoginResponseMsg.OK:
            raise Exception(r.message)



class LoginInfo(object):
    def __init__(self):
        self.email = None # Email addr is optional

class WebClient(object):
    def __init__(self, loginInfo):
        self.loginInfo = loginInfo
        self.ifnum = 0 # FIXME support multiple interfaces
        self.rxThread = None

    def connect(self, rxcallback, wantPipe = False):
        self.link = GCSHooks()

        u = self.loginInfo
        if not self.link.isUsernameAvailable(u.loginName):
            self.link.loginUser(u.loginName, u.password)
        else:
            self.link.createUser(u.loginName, u.password, u.email)

        allowctl = rxcallback != None
        if allowctl:
            self.rxThread = threading.Thread(target = lambda: self.__rxWorker(rxcallback), name = "webrx")
            self.rxThread.daemon = True
            self.rxThread.start()

        # FIXME - support multiple interfaces and different sysids
        sysid = 1
        self.link.setVehicleId(u.vehicleId, self.ifnum, sysid, allowctl, wantPipe = wantPipe)
        if not wantPipe:
            missionId = uuid.uuid1()
            self.link.startMission(True, missionId)

    def __rxWorker(self, rxcallback):
        logger.info("Listening to server")
        try:
            while True:
                e = self.link.readEnvelope()
                if e.mavlink != None:
                    for p in e.mavlink.packet:
                        #logger.debug("Received: " + p)
                        rxcallback(p)
        except:
            logger.error("Connection to server lost...")
            self.link = None

    def close(self):
        if self.link is not None:
            self.link.stopMission(True)
            elf.link.close()

    def filterMavlink(self, ifnum, bytes):
        if(self.link is not None):
            self.link.filterMavlink(ifnum, bytes)
