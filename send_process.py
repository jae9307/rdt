"""Implements GoBackN Sender"""
import socket
import struct
import time

def create_packet(src_port, dst_port, payload, seq_num):
    """
    Create a UDP packet

    :param src_port: port of the sender
    :param dst_port: port of the receiver
    :param payload: message being sent
    :param seq_num: sequence number of packet
    :return: the created packet
    """
    initial_checksum = 0
    length = 12 + len(payload)   # size of header is 12 bytes
    is_ack = False

    initial_packet = struct.pack('!HHLHBB', src_port, dst_port, seq_num,
                                 initial_checksum, length, is_ack)
    packet_with_payload = initial_packet + payload

    # Calculate the packet's checksum
    checksum = 0
    for index in range(0, len(packet_with_payload), 2):
        if index + 1 < len(packet_with_payload):
            chunk = struct.unpack('!H',
                                  packet_with_payload[index:index + 2])[0]
        else:
            chunk = struct.unpack('!H', packet_with_payload[index:index + 1]
                                  + b'\x00')[0]
        checksum += chunk
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF

    return struct.pack('!HHLHBB', src_port, dst_port, seq_num, checksum,
                       length, is_ack) + payload


def udt_send(packet, address, port):
    """
    Send a UDP packet to a given address and port

    :param packet: packet to send
    :param address: destination address
    :param port: destination port
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.sendto(packet, (address, port))
    finally:
        udp_socket.close()

def rdt_receive(address, local_port):
    """
    Attempt to receive a packet at the given address and port

    :param address: local address
    :param local_port: local port
    :return: the received packet
    """
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

def send_multiple(messages, start_index, num_to_send, sender_port,
                  receiver_port, address, network_proxy_port):
    """
    Send one or more packets

    :param messages: all messages the sender wants to send
    :param start_index: index to start sending messages from
    :param num_to_send: number of messages to send
    :param sender_port: local port
    :param receiver_port: destination port
    :param address: destination address
    :param network_proxy_port: network proxy port
    :return: timers for each packet sent
    """
    timers = []

    for index in range(start_index, start_index + num_to_send):
        message = (bytes(messages[index], encoding='utf-8'))
        timers.append(time.time())
        packet = create_packet(sender_port, receiver_port, message, index)
        print(f"Sender sending: {packet}")
        udt_send(packet, address, network_proxy_port)
        time.sleep(0.001)

    return timers

def rdt_sender_process(content):
    """
    Repeatedly send and receive packets using a sliding window

    :param content: content of file to send
    """
    address = socket.gethostbyname(socket.gethostname())
    sender_port = 23  # arbitrarily chosen number
    network_proxy_port = 19   # arbitrary number
    receiver_port = 67  # arbitrary number

    # Break file content into 8 byte messages
    messages = []
    for iterator in range(0, len(content), 8):
        if len(content[iterator:]) >= 8:
            messages.append(content[iterator:iterator+8])
        else:
            messages.append(content[iterator:])

    start_index = 0
    window_size = 4

    # Timers for sent packets
    timers = send_multiple(messages, start_index, window_size, sender_port,
                  receiver_port, address, network_proxy_port)

    window_end_index = 3  # index of last packet sent
    highest_acked_seq_num = -1

    timeout = 1
    try:
        while True:
            now = time.time()
            oldest_timer = timers[0]
            # If a packet times out, resend all packets in window
            if now - oldest_timer > timeout:
                print("---Timeout---")
                timers = send_multiple(messages, window_end_index
                                       - (window_size - 1), window_size,
                              sender_port, receiver_port, address,
                              network_proxy_port)

            packet = rdt_receive(address, sender_port)
            # If a packet is received, process and act accordingly
            if packet is not None:
                print(f"Sender Receiving: {packet}")
                (src_port, dst_port, seq_num, initial_checksum, length,
                 is_ack) = struct.unpack('!HHLHBB', packet[:12])
                print(f"Seq: {seq_num}")

                # If ACK for last message is received, end process
                if seq_num == len(messages) - 1:
                    break

                # ignore duplicate ACK
                elif seq_num > highest_acked_seq_num:
                    # Send number of packets equal to the received
                    # sequence number minus the highest previously
                    # ACKed sequence number (or however many packets
                    # are left if this is a lower amount)
                    num_to_send = seq_num - highest_acked_seq_num
                    if window_end_index + num_to_send <= len(messages) - 1:
                        new_timers = send_multiple(messages, window_end_index
                                                   + 1, num_to_send,
                                                   sender_port, receiver_port,
                                                   address,
                                                   network_proxy_port)
                        timers = timers[num_to_send:] + new_timers
                        window_end_index += num_to_send
                    elif len(messages) - 1 > window_end_index:
                        num_to_send = (len(messages) - 1) - window_end_index
                        new_timers = send_multiple(messages, window_end_index
                                                   + 1, num_to_send,
                                                   sender_port, receiver_port,
                                                   address,
                                                   network_proxy_port)
                        timers = timers[num_to_send:] + new_timers
                        window_end_index += num_to_send

                    highest_acked_seq_num = seq_num
    except KeyboardInterrupt:
        pass