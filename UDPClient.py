from socket import *
import re, uuid
from datetime import datetime, timedelta
import sys

serverName = 'localhost'
serverPort = 18000
clientSocket = socket(AF_INET, SOCK_DGRAM)

mac = uuid.getnode()
mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

message = input('Input lowercase sentence: ')
print()
message = message + " " + mac

clientSocket.sendto(message.encode(),(serverName, serverPort))

while True:

    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    modifiedMessage = modifiedMessage.decode()
    print (modifiedMessage)

    #extract mac address from client message 
    deconstruct = modifiedMessage.split(" ")
    DHCP_step = deconstruct[1]

    # here because deconstruct[2] will throw indexError when server responds with DECLINE message 
    if DHCP_step == "DECLINE":
        print("Client: Request was declined")
        clientSocket.close()
        sys.exit()

    client_mac_address = deconstruct[2]
    ip_addr = deconstruct[3]
    
    if DHCP_step == "OFFER":
        timestamp = deconstruct[4] + " " + deconstruct[5]
        timestamp_expir = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f') 
        if client_mac_address == mac.upper():
            
            now = datetime.now()
            difference = timestamp_expir - now
            
            if difference.total_seconds() > 0:
                client_info = f"{client_mac_address} {ip_addr} {timestamp_expir}"
                message = "REQUEST " + client_info 
                clientSocket.sendto(message.encode(),(serverName, serverPort))
                continue

    if DHCP_step == "DECLINE":
        print("Client: Request was declined")
        clientSocket.close()
        sys.exit()
    
    if DHCP_step == "ACKNOWLEDGE":
        timestamp = deconstruct[4] + " " + deconstruct[5]
        timestamp_expir = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        if client_mac_address == mac.upper():
            print()
            print(f"IP Address {ip_addr} has been assigned to this client. Expires at: {timestamp_expir}")
            print()
            
        else:
            print("Client: MAC Address does not match. TERMINATED.")
            print()
            clientSocket.close()
            sys.exit()

    message = input('Enter one of the following options in lowercase: release, renew, or quit')
    print()
    if message == "release":
        message = "RELEASE " + mac + " " + ip_addr
        clientSocket.sendto(message.encode(),(serverName, serverPort))
    if message == "renew":
        message = "RENEW " + mac + " " + ip_addr
        clientSocket.sendto(message.encode(),(serverName, serverPort))
    if message == "quit":
        clientSocket.close()
        sys.exit()
    
    
    

