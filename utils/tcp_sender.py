import time
import socket

def cal_lrc(msg):

    lrc = 0

    for v in msg:
        lrc ^= v
    
    return lrc

def vms_message(reversed):

    device_id = 0x01
    size_high = 0x00
    size_low = 0x08
    op_code = 0x27
    control = 0x80

    if reversed:
        data = 0x01
    else:
        data = 0x00

    header = [0x01, device_id]
    body = [0x02, size_high, size_low, op_code, control, data]
    lrc_code = cal_lrc(body)
    
    #message = header + body + [lrc_code, 0x03]
    message = body + [lrc_code, 0x03]
    message = bytearray(message)

    return message

def send_tcp(host, port, reversed):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
         
        client_socket.connect((host, port))
        print(f"TCP connected. ---> {host}:{port} ")

        client_socket.send(vms_message(reversed))
        print(f"TCP Send ---> Reversed : {reversed}")

        recv_data = client_socket.recv(1024)
        print(f"{recv_data.decode()}")
        
    except Exception as e:
        print(f"Exception: {e}")

    finally:
        client_socket.close()


if __name__ == "__main__":

    host = "192.168.1.20"
    port = 5000

    send_tcp(host, port, True)
    time.sleep(10)
    send_tcp(host, port, False)

    print("Test End.")