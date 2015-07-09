import os
import math
import pickle
import Image
import ImageFilter

from time import sleep
from twisted.python import log
from twisted.internet import task
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver

from threading import Lock

from cloud import utils
from cloud.common import *

class TransportWorkerProtocol(LineReceiver):
    def __init__(self, factory, homedir):
        self.factory = factory
        self.homedir = os.path.expanduser(homedir)
        self.name = str(self.factory.name)
        #self.MAX_LENGTH = 64000
        self.cswaiter = WaitForData(self.factory.fromCSServerToWorker, self.getData)
        self.ccwaiter = WaitForData(self.factory.fromCSClientToWorker, self.getReply)
        self.cswaiter.start()
        self.ccwaiter.start()
        self.mutexpr = Lock()
        self.mutexsp = Lock()
        self.fragments = None
        self.fragmentsLength = 0
        self.packetLength = 0
        self.work = None

    def getData(self, data):
        # strip off the length header
        self.sendPacket(data)

    def getReply(self, reply):
        # print "worker got OK, going for next", reply
        if "OK" in reply:
            print("DOWNLINKED")
            self.getWork(self.work)
        elif "NO" in reply:
            print("ERROR WHILE DOWNLINKING")
        else:
            print "Unokwn message"
            print reply
            
    def connectionMade(self):
        self.register()

    # line received
    def lineReceived(self, line):
        self.receivedMetadata(line)
        self.setRawMode()
        """
        fields = line.split(":")
        command = fields[0]
        if command == "DUMMY":
            pass
        elif command == "GET_MISSION":
            self.factory.fromWorkerToCSClient.put(line)
        elif command == "REGISTERED":
            self.registered(fields[1])
        elif command == "NO_WORK":
            self.noWork()
        elif command == "WORK":
            work = Work(fields[1], fields[2], fields[3], None)
            if work.job == "STORE":
                work.size = int(fields[4])
                self.fragments = None
                self.fragmentsLength = 0
                self.packetLength = work.size
                self.work = work
                self.setRawMode()
                return            
            elif work.job == "PROCESS":
                work.payload = fields[4]
            else:
                pass
            self.gotWork(work)
        else:
            print(line)
        """
    
    def receivedMetadata(self, metadata):
        print metadata
        fields = metadata.split(":")
        self.packetLength = fields.pop(0)
        self.chunks = []
        while fields:
            self.chunks.append(fields[0], fields[1])
            fields = fields[2:]

    def rawDataReceived(self, data):
        # buffer the the fragments
        if not self.fragments:
            self.fragments = data
            self.fragmentsLength = len(self.fragments)
        else:
            self.fragments = self.fragments + data
            self.fragmentsLength = self.fragmentsLength + len(data)
        # check if we received all the fragments
        if self.fragmentsLength == self.packetLength:
            print "YAHOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO!"
            
                    
    def rawDataReceivedOld(self, data):
        # buffer the the fragments
        if not self.fragments:
            self.fragments = data
            self.fragmentsLength = len(self.fragments)
        else:
            self.fragments = self.fragments + data
            self.fragmentsLength = self.fragmentsLength + len(data)
        # check if we received all the fragments
        if self.fragmentsLength == self.packetLength:
            self.setLineMode()
            self.work.payload = self.fragments
            self.gotWork(self.work)
                            
    # receive packet    
    def packetReceived(self, packet):
        # acquire the mutex
        self.mutexpr.acquire()
        log.msg(packet)
        if self.name == "Worker" and packet.flags == REGISTERED:
            self.registered(packet)
        elif packet.destination == "Server":
            self.forwardToServer(packetstring)
        elif packet.destination != self.name:
            self.forwardToChild(packet)
        elif packet.flags == "NO_WORK":
            self.noWork()
        elif packet.flags == "WORK":
            self.gotWork(packet.payload)
        elif packet.flags == CHUNK:
            self.receivedChunk(packet)
        else:
            log.msg("Server said: %s" % packetstring)
        # release the mutex
        self.mutexpr.release()
    
    # send a packet, if needed using multiple fragments
    def sendPacket(self, packetstring):
        self.mutexsp.acquire()
        length = len(packetstring)
        packetstring = str(length).zfill(LHSIZE) + packetstring
        for i in range(int(math.ceil(float(length)/MAX_PACKET_SIZE))):
            # log.msg("Sending a fragment")
            self.transport.write(packetstring[i*MAX_PACKET_SIZE:(i+1)*MAX_PACKET_SIZE])
        self.mutexsp.release()
    
    def register(self):
        self.sendLine("REGISTER:" + self.name)
        
    def registered(self, name):
        self.name = name
        self.homedir = self.homedir + str(self.name) + "/"
        try:
            os.mkdir(self.homedir)
        except OSError:
            log.msg("OSError: Unable to create home directory, exiting")
            exit()
        self.status = IDLE

    def heartbeat(self):
        pass
        
    def deregister(self):
        self.transport.loseConnection()

    def getWork(self, work = None):
        print("Worker requesting work")
        if work:
            log.msg("Finished work")
            workstr = "WORK:" + self.name + ":" + work.tostr() + LONGLOREMIPSUM
            log.msg(workstr)
            self.sendLine(workstr)
            log.msg("sent request for work")
        else:
            self.sendLine("WORK:" + self.name + ":")
    
    def noWork(self):
        log.msg("No work")
        task.deferLater(reactor, 1.0, self.getWork)
    
    def gotWork(self, work):
        log.msg("Worker got work")
        if work.job == "STORE":
            self.store(work)
        elif work.job == "PROCESS":
            self.process(work)
        elif work.job == "DOWNLINK":
            self.downlink(work)
        else:
            log.msg("Unkown work")
            log.msg(work)

    def store(self, work):
        # create the directory, if needed
        directory = self.homedir + os.path.split(work.filename)[0]
        if not os.path.exists(directory):
            os.mkdir(directory)
        chunk = open(self.homedir + work.filename, "w")
        chunk.write(work.payload)
        chunk.close()
        work.payload = None
        self.getWork(work)
    
    def process(self, work):
        log.msg(work)
        # create the directory, if needed
        directory = self.homedir + work.payload + "/"
        if not os.path.exists(directory):
            os.mkdir(directory)
        filename = self.homedir + work.filename
        image = Image.open(filename)
        edges = image.filter(ImageFilter.FIND_EDGES)
        edges.save(directory + os.path.split(work.filename)[1])
        self.getWork(work)
        
    def downlink(self, work):
        filename = self.homedir + work.filename
        log.msg(filename)
        data = open(filename).read()
        log.msg(work)
        work.payload = str(len(data))
        metadata = "CHUNK:" + work.tostr()
        self.forwardToServer(metadata, data)
        self.work = work
        print("wait for downlink ack to call getWork")
        self.getWork(self.work)
                   
    def forwardToServer(self, metadata, data):
        print "worker: forwarded to csclient"
        self.factory.fromWorkerToCSClient.put(metadata)
        self.factory.fromWorkerToCSClient.put(data)
   
    def forwardToChild(self, packet):
        self.factory.fromWorkerToCSServer.put(packet)

            
class TransportWorkerFactory(protocol.ClientFactory):
    def __init__(self, name, homedir, fromWorkerToCSClient, fromCSClientToWorker, fromWorkerToCSServer, fromCSServerToWorker):
        self.name = name
        self.homedir = homedir
        self.fromWorkerToCSClient = fromWorkerToCSClient
        self.fromCSClientToWorker = fromCSClientToWorker
        self.fromWorkerToCSServer = fromWorkerToCSServer
        self.fromCSServerToWorker = fromCSServerToWorker
        
    def buildProtocol(self, addr):
        return TransportWorkerProtocol(self, self.homedir)
        
    def clientConnectionFailed(self, connector, reason):
        log.msg("Connection failed.")
        reactor.stop()
        
    def clientConnectionLost(self, connector, reason):
        log.msg("Connection lost.")
        reactor.stop()
