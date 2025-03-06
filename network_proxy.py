import socket
import struct


def recieve(address, local_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((address, local_port))

    packet = None

    try:
        packet, addr = udp_socket.recvfrom(65565)
    finally:
        udp_socket.close()

    return packet

def forward(packet, address, dst_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.sendto(packet, (address, dst_port))
    finally:
        udp_socket.close()

def act_as_network():
    address = socket.gethostbyname(socket.gethostname())
    network_proxy_port = 19  # arbitrarily chosen number
    receiver_port = 67   # arbitrary number
    sender_port = 23   # arbitrary number

    while True:
        packet = recieve(address, network_proxy_port)
        print(f"Network: {packet}")

        # TODO: mess up packet in some way

        src_port, dst_port, seq_num, initial_checksum, length, is_ack = struct.unpack('!HHLHBB', packet[0:12])
        forward(packet, address, dst_port)

def main():
    act_as_network()

if __name__ == '__main__':
    main()