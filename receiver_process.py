"""Implements GoBackN Receiver"""
import socket
import struct
import server

def rdt_recieve(address, local_port):
    """
    Attempt to receive a packet at the given address and port

    :param address: local address
    :param local_port: local port
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

def validate_checksum(packet):
    """
    Calculate packet's checksum to see if it's been corrupted

    :param packet: packet to validate
    :return: True if packet hasn't been corrupted, False otherwise
    """
    checksum = 0
    for index in range(0, len(packet), 2):
        if index + 1 < len(packet):
            chunk = struct.unpack('!H', packet[index:index + 2])[0]
        else:
            chunk = struct.unpack('!H', packet[index:index + 1] + b'\x00')[0]
        checksum += chunk
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF

    if checksum == 0:
        return True
    else:
        print(f"Checksum is invalid: {checksum}")
        return False

def rdt_receiver_process():
    """Repeatedly receive and send packets"""
    file1 = open("output.txt", "w")  # append mode
    file1.write("")
    file1.close()

    address = socket.gethostbyname(socket.gethostname())
    receiver_port = 67   # arbitrary number
    network_proxy_port = 19  # arbitrarily chosen number
    sender_port = 23  # arbitrarily chosen number

    highest_acked_seq_num = -1
    is_ack = True

    try:
        while True:
            packet = rdt_recieve(address, receiver_port)
            # If a packet is received, process and act accordingly
            if packet is not None:
                print(f"Receiver Receiving: {packet}")
                src_port, dst_port, seq_num, checksum, length\
                    = struct.unpack('!HHLHB', packet[:11])
                payload = packet[12:]

                checksum_valid = validate_checksum(packet)

                # If received packet has expected sequence number and
                # hasn't been corrupted, increment the highest ACKed
                # sequence number
                if seq_num - 1 == highest_acked_seq_num and checksum_valid:
                    highest_acked_seq_num += 1
                    server.forward(payload)
                elif highest_acked_seq_num == -1:
                    continue

                send_packet = (struct.pack('!HHLHBB', receiver_port,
                                           sender_port, highest_acked_seq_num,
                                           checksum, length, is_ack)
                               + payload)
                udt_send(send_packet, address, network_proxy_port)
    except KeyboardInterrupt:
        pass

def main():
    """Call receiver_process"""
    rdt_receiver_process()

if __name__ == '__main__':
    main()