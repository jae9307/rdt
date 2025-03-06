import socket
import struct
import time

def create_packet(src_port, dst_port, payload):

    initial_checksum = 0
    length = 12 + len(payload)   # size of header is 12 bytes
    is_ack = False
    seq_num = 0


    initial_packet = struct.pack('!HHLHBB', src_port, dst_port, seq_num,
                                 initial_checksum, length, is_ack)
    packet_with_payload = initial_packet + payload

    # Calculate the packet's checksum
    checksum = 0
    # for index in range(0, len(packet_with_payload), 2):
    #     checksum += ((packet_with_payload[index] << 8)
    #                  + packet_with_payload[index + 1])
    # checksum = (checksum >> 16) + (checksum & 0xFFFF)
    # checksum = ~checksum & 0xFFFF

    return (packet_with_payload[:6] + struct.pack('!H', checksum)
            + packet_with_payload[8:])


def udt_send(packet, address, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.sendto(packet, (address, port))
    finally:
        udp_socket.close()

def rdt_receive(address, local_port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((address, local_port))
    # udp_socket.settimeout(3)

    try:
        packet, addr = udp_socket.recvfrom(65565)
    finally:
        udp_socket.close()

    return packet

def rdt_sender_process():
    address = socket.gethostbyname(socket.gethostname())
    sender_port = 23  # arbitrarily chosen number
    network_proxy_port = 19   # arbitrary number
    receiver_port = 67  # arbitrary number
    payload = bytes("test string", encoding='utf-8')

    packet = create_packet(sender_port, receiver_port, payload)

    start_time = time.time()
    udt_send(packet, address, network_proxy_port)

    packet = rdt_receive(address, sender_port)

    print(f"Ack: {packet}")

def main():
    rdt_sender_process()

if __name__ == '__main__':
    main()