import socket

def rdt_recieve(address, local_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((address, local_port))

    packet = None

    try:
        packet, addr = udp_socket.recvfrom(65565)
    finally:
        udp_socket.close()

    return packet

def rdt_receiver_process():
    address = socket.gethostbyname(socket.gethostname())
    receiver_port = 67   # arbitrary number

    packet = rdt_recieve(address, receiver_port)

    print(f"Packet: {packet}")

def main():
    rdt_receiver_process()

if __name__ == '__main__':
    main()