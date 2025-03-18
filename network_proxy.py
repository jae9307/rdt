import socket
import struct
import time


def recieve(address, local_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((address, local_port))
    udp_socket.settimeout(0.001)

    packet = None

    try:
        packet, addr = udp_socket.recvfrom(65565)
    except OSError:
        pass
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

    queue = []

    start_time = time.time()
    while True:
        # print(f"Receiving: {time.time()}")
        packet = recieve(address, network_proxy_port)
        if packet is not None:
            print(f"Network: {packet}")
            queue.append(packet)

        # TODO: mess up packet in some way

        now = time.time()
        # print(f"time: {now - start_time}")
        if now - start_time >= 0.09 and len(queue) > 0:
            send_packet = queue.pop(0)
            src_port, dst_port, seq_num, initial_checksum, length, is_ack = struct.unpack('!HHLHBB', send_packet[0:12])
            forward(send_packet, address, dst_port)
            start_time = time.time()

def main():
    act_as_network()

if __name__ == '__main__':
    main()