import socket
import hashlib
import requests

serverPort = 50000
ip_addr = socket.gethostbyname(socket.gethostname())
delimiter = "[]:[]"


packetLoss = True
if packetLoss == True :
    print("Checksum mismatch detected or dropping packet")
def GETrequest(url):
    URL = url
    x = requests.get(URL)
    print(x.status_code)
    print("get\n")


def POSTrequest(URL, MYOBJ):
    url = URL
    myobj = MYOBJ
    x = requests.post(url, json=myobj)
    print(x.text)
    print("post\n")
url1=GETrequest(" https://www.google.com")
while True:

    clientSocekt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #setting the time out
    clientSocekt.settimeout(5)
    server_address = (ip_addr, serverPort)
    #taking the file name as input from the client
    file = input("Please, enter the file name: ")
    message = file
    seqNumberFlag = 0 #Initialized to zero
    f = open("new_" + file, 'w')

    try:
        connection_count = 0 #trails
        #sending the desired file to the server.
        sent = clientSocekt.sendto(message.encode('utf-8'), server_address)
        while True:
            print ('Waiting for the server response.....')
            try:
                #getting the server response and the server address.
                data, server = clientSocekt.recvfrom(1024)
                connection_count = 0
            #if the conncection failed, try to connect again.
            except:
                connection_count += 1
                if connection_count < 4:
                    print ("Connection time out, retrying again..")
                    continue
                else:
                    print ("Maximum connection trials reached, please choose another request")
                    break
            #getting the sequence number
            sequenceNumber = data.decode().split(delimiter)[1]
            #getting the check sum of the data sent
            checksum = hashlib.sha1(data.decode().split(delimiter)[3].encode('utf-8')).hexdigest()
            #comparing the server and the clients checksums, seqnumbers and packet length
            if data.decode().split(delimiter)[0] == checksum and seqNumberFlag == int(sequenceNumber == True):
                packetLength = data.decode().split(delimiter)[2]
                #couldn't find the file 
                if data.decode().split(delimiter)[3] == "NULL":
                    print ("Requested file could not be found on the server, please choose another file")
                else: #file found, starting writing the data
                    f.write(data.decode().split(delimiter)[3])
                print(f"Sequence number: {sequenceNumber}")
                print (f"Message Length: {packetLength}")
                #sending ack to the server..
                sent = clientSocekt.sendto((str(sequenceNumber) + "," + packetLength).encode('utf-8'), server)
            else: #packets are not matching
                print ("Checksum mismatch detected or dropping packet")
                continue
            #for the last packet to be sent
            if int(packetLength) < 500:
                sequenceNumber = int(not sequenceNumber)
                break

    finally:
        print ("Closing the socket.")
        clientSocekt.close()
        f.close()