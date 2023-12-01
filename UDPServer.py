from socket import *
from datetime import datetime, timedelta

serverPort = 18000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

class client(object):
    def __init__(self, IP_address=None, MAC_address=None, timeStamp=None, 
        Acked=None):
        self.IP_address = IP_address
        self.MAC_address =  MAC_address
        self.timeStamp = timeStamp
        self.Acked = Acked

        
    def setTimeStamp(self):
        timestamp = datetime.now() + timedelta(seconds=60)
        self.timeStamp = timestamp

ip = "192.168.45."
ip_addr = ["14","13","12","11","10","9","8","7","6","5","4","3","2","1"]
records = {}

newLine = '\n'

print('The server is ready to receive\n')

while 1:
    
    #message contains client message and MAC Address. 
    # ClientAddress = ip add & port number
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode().upper()
    print(modifiedMessage)
    print()
    if modifiedMessage == "ADMIN":
        modifiedMessage = ""
        for i in records:
            
            modifiedMessage += f"MAC address: {records[i].MAC_address} IP Address: {records[i].IP_address}, Timestamp: {records[i].timeStamp}, Acknowledged: {records[i].Acked}{newLine}"
        serverSocket.sendto(modifiedMessage.encode(), clientAddress)
        continue
    
    #extract mac address from client message 
    deconstruct = modifiedMessage.split(" ")
    DHCP_step = deconstruct[0]
    client_mac_address = deconstruct[1]

    #case that mac address is already assigned an ip 
    if DHCP_step == "DISCOVER":
        print(f"Server: client with mac address {client_mac_address} is discovering")
            
        #checks for Mac address in the server records
        if client_mac_address in records:
                
            #if mac address is found and timestamp has not expired then send ACKNOWLEDGE message to client
            now = datetime.now()
            difference = records[client_mac_address].timeStamp - now
            
            # difference > 0 means timeStamp has not expired
            if(difference.total_seconds() > 0):
                client_info = f"{client_mac_address} {records[client_mac_address].IP_address} {records[client_mac_address].timeStamp}"
                modifiedMessage = "Server: ACKNOWLEDGE " + client_info
                serverSocket.sendto(modifiedMessage.encode(), clientAddress)
                        
            # else send client OFFER message including mac address, ip address and timestamp
            else:
                records[client_mac_address].setTimeStamp()      
                client_info = f"{client_mac_address} {records[client_mac_address].IP_address} {records[client_mac_address].timeStamp}"
                modifiedMessage = "Server: OFFER " + client_info
                serverSocket.sendto(modifiedMessage.encode(), clientAddress)

        # if IP Address is available then assigns client an IP and sends OFFER  
        else:            
            if  ip_addr:
                
                timestamp = datetime.now() + timedelta(seconds=60)
                assigned_IP = ip + ip_addr.pop()
                new_record = {client_mac_address: client(assigned_IP, client_mac_address, timestamp, False)}
                records.update(new_record)
                
                client_info = f"{client_mac_address} {records[client_mac_address].IP_address} {records[client_mac_address].timeStamp}"
                #print("line 82")
                modifiedMessage = "SERVER: OFFER " + client_info
                serverSocket.sendto(modifiedMessage.encode(), clientAddress)

    if DHCP_step == "REQUEST":
        requested_ip = deconstruct[2]
        # if Requested IP == client IP in records then send client Acknowledge message
        
        if records[client_mac_address].IP_address == requested_ip:
           
            now = datetime.now()
            difference = records[client_mac_address].timeStamp - now
    
            if(difference.total_seconds() > 0):
             
                records[client_mac_address].Acked = True      
                client_info = f"{client_mac_address} {records[client_mac_address].IP_address} {records[client_mac_address].timeStamp}"
                modifiedMessage = "SERVER: ACKNOWLEDGE " + client_info
                print(modifiedMessage)
                serverSocket.sendto(modifiedMessage.encode(), clientAddress)
                    
            # else send client DECLINE message
            else:
                modifiedMessage = "SERVER: DECLINE" 
                serverSocket.sendto(modifiedMessage.encode(), clientAddress)
         
        else:
            modifiedMessage = "SERVER: DECLINE" 
            serverSocket.sendto(modifiedMessage.encode(), clientAddress)
   
    if DHCP_step == "RELEASE":
            modifiedMessage = "SERVER to client: IP was released"
            # Release IP Address of client if found
            if client_mac_address in records:
                
                if records[client_mac_address].Acked == False:
                    print(f"SERVER: IP ADDRESS {records[client_mac_address].IP_address} has already been released")
                    print()
                    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
                else:
                    records[client_mac_address].Acked = False
                    records[client_mac_address].timeStamp = datetime.now()  # setting timestamp to current time indicates IP assingment has expired
                    print(f"SERVER: IP ADDRESS {records[client_mac_address].IP_address} has been released")
                    print()
                    serverSocket.sendto(modifiedMessage.encode(), clientAddress)

                for i in records:
                    print(f"{records[i].MAC_address} {records[i].IP_address} {records[i].timeStamp} {records[i].Acked}")
                
    if DHCP_step == "RENEW":

        if client_mac_address in records:
            records[client_mac_address].setTimeStamp()
            records[client_mac_address].Acked = True
            
            client_info = f"{client_mac_address} {records[client_mac_address].IP_address} {records[client_mac_address].timeStamp}"
            modifiedMessage = "SERVER: ACKNOWLEDGE " + client_info
            serverSocket.sendto(modifiedMessage.encode(), clientAddress)
            continue
        else:  
            if ip_addr:

                timestamp = datetime.now() + timedelta(seconds=60)
                assigned_IP = ip + ip_addr.pop()
                new_record = {client_mac_address: client(assigned_IP, client_mac_address, timestamp, False)}
                records.update(new_record)
                
                client_info = f"{client_mac_address} {records[client_mac_address].IP_address} {records[client_mac_address].timeStamp}"
                modifiedMessage = "SERVER: OFFER " + client_info
                serverSocket.sendto(modifiedMessage.encode(), clientAddress)
                continue
            else:
                
                for expired_ip in records:
                
                    now = datetime.now()
                    difference = expired_ip.timeStamp - now
                    
                    # difference < 0 means timeStamp has expired
                    if(difference.total_seconds() < 0):
                        
                        expired_ip.Acked = False
                        expired_ip.setTimeStamp
                        expired_ip.MAC_address = client_mac_address

                        records[client_mac_address] = records.pop(expired_ip)

                        client_info = f"{client_mac_address} {records[client_mac_address].IP_address} {records[client_mac_address].timeStamp}"
                        modifiedMessage = "Server: OFFER " + client_info
                        serverSocket.sendto(modifiedMessage.encode(), clientAddress)   
                        continue
        modifiedMessage = "Server: DECLINE"
        serverSocket.sendto(modifiedMessage.encode(), clientAddress)

