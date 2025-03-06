import socket
import struct


def rdt_recieve(address, local_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((address, local_port))

    packet = None

    try:
        packet, addr = udp_socket.recvfrom(65565)
    finally:
        udp_socket.close()

    return packet

def udt_send(packet, address, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.sendto(packet, (address, port))
    finally:
        udp_socket.close()

def rdt_receiver_process():
    address = socket.gethostbyname(socket.gethostname())
    receiver_port = 67   # arbitrary number
    network_proxy_port = 19  # arbitrarily chosen number
    sender_port = 23  # arbitrarily chosen number

    packet = rdt_recieve(address, receiver_port)
    print(f"Original: {packet}")

    # TODO: verify that packet isn't messed up
    is_ack = True
    packet = struct.pack('!HH', receiver_port, sender_port) + packet[4:11] + struct.pack('!B', is_ack) + packet[12:]

    udt_send(packet, address, network_proxy_port)

def main():
    rdt_receiver_process()

if __name__ == '__main__':
    main()