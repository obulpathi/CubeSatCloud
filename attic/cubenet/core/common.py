#!/usr/bin/env python

from collections import namedtuple

# formats
# Chunk = (ID, CHUNK_SIZE, CubeSat)
# Packet = (sender, receiver, source, destination, datatype, payload, latency, size)

# GENERAL CONSTANTS
KB = 1024
KBPS = 1024
MB = 1048576
MBPS = 1048576
GB = 1073741824
GHz = 1000000000
MILLION = 1000000
BILLION = 1000000000

# chunk constants
CHUNK_SIZE = 65536
CHUNK_VARIATION = 16384

# commands
ACK = "ACK"
CHUNK = "CHUNK"
NEW_CHUNK = "NEW_CHUNK"
BAD_PACKET = "BAD_PACKET"
LAST_PACKET = "LAST_PACKET"
DUMMY_PAYLOAD = "DUMMY_PAYLOAD"
FINISHED_CHUNK = "FINISHED_CHUNK"
COMMAND_IMAGE_DOWNLINK = "COMMAND_IMAGE_DOWNLINK"
COMMAND_IMAGE_PROCESS_DOWNLINK = "COMMAND_IMAGE_PROCESS_DOWNLINK"

# Link Layer definitions
LL_ACK = "LL_ACK"
LL_END_ACK = "LL_END_ACK"
LL_BAD_PACKET = "LL_BAD_PACKET"
LL_END_PACKET = "LL_END_PACKET"

# FSM States
IDLE     = "IDLE"
STARTING = "STARTING"
WORKING  = "WORKING"
WAITING  = "WAITING"
FAILURE  = "FAILURE"
FINISHED = "FINISHED"
TRANSMIT = "TRANSMIT"
RECEIVE  = "RECEIVE"

# battery
BATTERY_LOW = 100

# Communication channel models
Link = namedtuple('Link', 'datarate mtu latency overhead')
S2GSLink = Link(10 * MBPS, MB, 100, 64)
GS2SLink = Link(10 * MBPS, MB, 100, 64)
GS2CSLink = Link(9600, MB, 5, 64)
CS2GSLink = Link(9600, MB, 5, 64)
CS2CSLink = Link(MBPS, MB, 2, 64)

# tasks, fileops, ... 
Task = namedtuple('Task', 'ID flops')
Fileops = namedtuple('Fileops', 'ID filename mode data')
Configuration = namedtuple('Configuration', 'processor memory battery nic transciever power location tle')

# mission commands
Torrent = namedtuple('Torrent', 'payload size chunks')
MapReduce = namedtuple('MapReduce', 'payload size chunks')

# subsystems
"""
Processor = namedtuple('Processor', 'MIPS clock tasks')
NIC = namedtuple('NIC', 'bandwidth transmit_queues rxPacket')
Memory = namedtuple('Memory', 'capacity diskspeed tasks')
Transciever = namedtuple('Transciever', 'datarate tasks')
Battery = namedtuple('Battery', 'capacity charge chargerate current_limit')
"""
Power = namedtuple('Power', 'processor memory nic transciever eps maintainance')
"""
Location = namedtuple('Location', 'x y')
"""

class Chunk(object):
    def __init__(self, id, size, slave):
        self.id = id
        self.size = size
        self.slave = slave
    def __repr__(self):
        return "ID: " + str(self.id) + ", Size: " + str(self.size) + ", Slave: " + str(self.slave)
        
class Packet(object):
    def __init__(self, sender, receiver, source, destination, datatype, id, payload, size, flags = None):
        self.sender = sender
        self.receiver = receiver
        self.source = source
        self.destination = destination
        self.datatype = datatype
        self.id = id
        self.payload = payload
        self.size = size
        self.flags = flags
        
    def __repr__(self):
        return "Sender: " + str(self.sender.name) + ", Receiver: " + str(self.receiver.name) + ", Source: " + str(self.source.name) + ", Destination: " + str(self.destination.name) + ", Datatype: " + str(self.datatype) + ", ID: " + str(self.id) + ", Payload: " + str(self.payload) + ", Size: " + str(self.size)

class LLPacket(object):
    def __init__(self, id, size, payload, flags = 0x00):
        self.id = id
        self.size = size
        self.payload = payload
        self.flags = flags
        
    def __repr__(self):
        return "ID: " + str(self.id) + ", Size: " + str(self.size) + ", Payload: " + str(self.payload) + ", Flags: " + str(self.flags)

class Processor(object):
	def __init__(self, MIPS, clock, tasks):
		self.MIPS = MIPS
		self.clock = clock
		self.tasks = tasks

class NIC(object):
	def __init__(self, bandwidth, transmit_queues, rxPacket):
		self.bandwidth = bandwidth
		self.transmit_queues = transmit_queues
		self.rxPacket = rxPacket

class Memory(object):
	def __init__(self, capacity, diskspeed, tasks):
		self.capacity = capacity
		self.diskspeed = diskspeed
		self.tasks = tasks

class Transciever(object):
	def __init__(self, datarate, tasks):
		pass

class Battery(object):
	def __init__(self, capacity, charge, chargerate, current_limit):
		self.capacity = capacity
		self.charge = charge
		self.chargerate = chargerate
		self.current_limit = current_limit

"""
class Power(object):
	def __init__(self, processor, memory, nic, transciever, eps):
		pass
"""

class Location(object):
	def __init__(self, x, y):
		pass

# Queue constructs
class QItem(object):
    def __init__(self, item, timer):
        self.item = item
        self.timer = timer
    def __repr__(self):
       return "Item: " + str(self.item) + "Timer: " + str(self.timer) 
        
def processQueue(queue, qname, logger):
    if queue:
        logger.debug(qname + " status: Item: " + str(queue[0].item) + " Timer: " + str(queue[0].timer))
        queue[0].timer = queue[0].timer - 1
        if queue[0].timer <= 0:
            element = queue[0]
            queue.remove(element)
            return element.item

# configuration
processor = Processor(GHz, GHz, None)
memory = Memory(32 * GB, 10 * MBPS, None)
battery = Battery(1000, 500, 10, 10)
nic = NIC(100, None, None)
transciever = Transciever(100, None)
power = Power(10, 10, 10, 10, 10, 5)
location = Location(0, 0)
tle = None

master_configuration = Configuration(processor, memory, battery, nic, transciever, power, location, tle)
slave_configuration = Configuration(processor, memory, battery, nic, transciever, power, location, tle)
