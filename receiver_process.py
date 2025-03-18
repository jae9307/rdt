import socket
import struct
import time


def rdt_recieve(address, local_port):
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

    queue = []

    start_time = time.time()
    while True:
        # print(f"Receiving: {time.time()}")
        packet = rdt_recieve(address, receiver_port)
        if packet is not None:
            print(f"Original: {packet}")
            queue.append(packet)

        now = time.time()
        # print(f"time: {now - start_time}")
        if now - start_time >= 0.001 and len(queue) > 0:
            # TODO: verify that packet isn't messed up
            is_ack = True
            send_packet = queue.pop()
            queue = []
            send_packet = struct.pack('!HH', receiver_port, sender_port) + send_packet[4:11] + struct.pack('!B', is_ack) + send_packet[12:]

            udt_send(send_packet, address, network_proxy_port)

def main():
    rdt_receiver_process()

if __name__ == '__main__':
    main()