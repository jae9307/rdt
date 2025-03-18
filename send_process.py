import socket
import struct
import time

def create_packet(src_port, dst_port, payload, ack_num):

    initial_checksum = 0
    length = 12 + len(payload)   # size of header is 12 bytes
    is_ack = False
    seq_num = 0


    initial_packet = struct.pack('!HHLHBBB', src_port, dst_port, seq_num,
                                 initial_checksum, length, is_ack, ack_num)
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
    udp_socket.settimeout(0.001)

    packet = None

    try:
        packet, addr = udp_socket.recvfrom(65565)
    except OSError:
        pass
    finally:
        udp_socket.close()

    return packet

def rdt_sender_process():
    address = socket.gethostbyname(socket.gethostname())
    sender_port = 23  # arbitrarily chosen number
    network_proxy_port = 19   # arbitrary number
    receiver_port = 67  # arbitrary number

    messages = []

    start_time = time.time()
    for index in range(4):
        message = (bytes(f"test string{index}", encoding='utf-8'))
        packet = create_packet(sender_port, receiver_port, message, index)
        print(f"Sending: {time.time()}")
        udt_send(packet, address, network_proxy_port)
        time.sleep(0.001)

    while True:
        # print(f"Receiving: {time.time()}")
        packet = rdt_receive(address, sender_port)
        if packet is not None:
            print(f"Ack: {packet}")

    # end_time = time.time()
    #
    # print(f"Elapsed: {end_time - start_time}")

def main():
    rdt_sender_process()

if __name__ == '__main__':
    main()