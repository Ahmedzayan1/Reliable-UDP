import socket
import threading
import hashlib
import time

#Global variables.
#server port 
serverPort = 50000
#The ip address of the running device.
ip_addr = socket.gethostbyname(socket.gethostname())
#delimiter to be used between the header elements.
delimiter = "[]:[]"
packetLoss = False

class packet():
    checksum = 0
    sequenceNumber = 0
    length = 0
    message = 0

    #To make the packet.
    def makePacket(self, data):
        #getting the checksum in a hexdigest format
        self.checksum = hashlib.sha1(data.encode('utf-8')).hexdigest()
        #getting the message length
        self.length = str(len(data))
        self.message = data
        print (f"Message Length:{self.length} \nSequence Number: {self.sequenceNumber}")


#function to handle the client requests.
def handle_client(address, data):
    endPacket = 0 #A flag to know the end of the
    packet_count = 0 
    time.sleep(0.5)

    pkt = packet() #initialize the packet
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        print (f"Opening the file: {data.decode()}")
        #open the file the client requested
        file = open(data.decode(), 'r')
        data = file.read() #read the file
        file.close()
    except: #if the file the client requested couldn't be found
        message = "NULL"
        #making the packet.
        pkt.makePacket(message)
        #preparing the response of the server to be sent to the client
        lastPacket = str(pkt.checksum) + delimiter + str(pkt.sequenceNumber) + delimiter + str(pkt.length) \
                     + delimiter + pkt.message
        serverSocket.sendto(lastPacket.encode('utf-8'), address)
        print ("Requested file could not be found...")
        return

    x = 0 #used to chunk the data
    while True:
        packet_count += 1
        #getting 500 bytes out of the data each time. 
        message = data[x * 500:x * 500 + 500]
        pkt.makePacket(message)
        lastPacket = str(pkt.checksum) + delimiter + str(pkt.sequenceNumber) + delimiter + str(
            pkt.length) + delimiter + pkt.message
        sent = serverSocket.sendto(lastPacket.encode('utf-8'), address)
        print (f'Sent: {sent} bytes to {address}, and now awaiting for acknowledgment')
        
        #setting the time out.
        serverSocket.settimeout(2)
        try:
            #recieving the acknowledgment from the client.
            ack, address = serverSocket.recvfrom(200)    
        except:
            print (f"Time out reached, resending the last packet: {x} again.")
            packet_count -= 1
            continue
        #if the ack number = to the sequence number, continue on sending the next packet and toggle the seq number value
        if ack.decode().split(",")[0] == str(pkt.sequenceNumber):
            pkt.sequenceNumber = int(not pkt.sequenceNumber) #check seq no.
            print (f"Acknowledged by: {ack.decode()}")
            endPacket = ack.decode().split(",")[1]
            x += 1
            #to know the last packet that needs to be sent.
            if int(endPacket) < 500:
                print (f"Packets served: {packet_count} ")
                break

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (ip_addr, serverPort)
print (f'Connected to: {ip_addr} , port {serverPort}')
#Bind the ip address with the socket.
sock.bind(server_address)
while True:
    print ('Waiting to receive message')
    #wait for the connection and save the conn to send data if needed to the client and addr for the ip address of the client
    data, address = sock.recvfrom(600)
    #Running multibe clients at a time..
    connectionThread = threading.Thread(target=handle_client, args=(address, data))
    connectionThread.start()
    print ('Received %s bytes from %s' % (len(data), address))