import socket
import time
import json

print('Starting the UDP client ~~~')
UDPclient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPclient.bind(('127.0.0.1', 7072))
UDPclient.settimeout(5)
# f=open("udpr.txt","w")
while True:
    try:
        data, server = UDPclient.recvfrom(2000)
        # print("RXD :", data[:100])
        data = data.decode("utf-8")
        print("RXD :", data)
        # f.write(f'\n{data}')
    except Exception as e:
        print("Excepttion Interrupt ~~~", e)
        time.sleep(1)
        continue
    except KeyboardInterrupt:
        print("KeyboardInterrupt ~~")
        break
# f.close()
UDPclient.close()