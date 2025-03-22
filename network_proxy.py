"""Simulate network conditions"""
import socket
import struct
import time
import argparse

def recieve(address, local_port):
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

def forward(packet, address, dst_port):
    """
    Forward received packet to its destination

    :param packet: packet to send
    :param address: destination address
    :param dst_port: destination port
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.sendto(packet, (address, dst_port))
    finally:
        udp_socket.close()

def act_as_network(args):
    """
    Repeatedly receive packets and send them to their destination

    :param args: command line arguments for manipulating packets
    """
    address = socket.gethostbyname(socket.gethostname())
    network_proxy_port = 19  # arbitrarily chosen number

    queue = []

    start_time = time.time()
    drop_time = time.time()
    corrupt_time = time.time()
    reorder_time = time.time()

    try:
        while True:
            # If a packet is received, add it to the queue
            packet = recieve(address, network_proxy_port)
            if packet is not None:
                print(f"Network Receiving: {packet}")
                queue.append(packet)

            # Forward a packet after a short interval
            now = time.time()
            if now - start_time >= 0.09 and len(queue) > 0:
                send_packet = queue.pop(0)
                src_port, dst_port, seq_num, initial_checksum, length, is_ack\
                    = struct.unpack('!HHLHBB', send_packet[0:12])
                forward(send_packet, address, dst_port)
                start_time = time.time()

            # After defined number of seconds, drop a packet
            if (args.drop and now - drop_time > float(args.drop)
                    and len(queue) > 0):
                packet_found = False
                packet_index = 0

                # Find a packet sent by the sender_process
                while (not packet_found and len(queue) - 1
                       >= packet_index):
                    first_packet = queue[packet_index]

                    is_ack = struct.unpack('!B', first_packet[11:12])[0]

                    if not packet_found:
                        if is_ack:
                            packet_index += 1
                        else:
                            packet_found = True

                if packet_found:
                    print(f"Popping {queue.pop(packet_index)}")
                drop_time = time.time()

            # After defined number of seconds, corrupt a packet's data
            if (args.corrupt and now - corrupt_time > float(args.corrupt)
                    and len(queue) > 0):
                packet = queue.pop()
                print(f"corrupting {packet}")
                queue.append(struct.pack('!H', 678) + packet[2:])
                corrupt_time = time.time()

            # After defined number of seconds, reorder two packets
            if (args.reorder and now - reorder_time > float(args.reorder)
                    and len(queue) > 1):
                first_packet_found = False
                second_packet_found = False
                first_packet_index = 0
                second_packet_index = 1
                first_packet = None
                second_packet = None

                # Find two packets sent by the sender_process
                while not first_packet_found and not second_packet_found\
                        and len(queue) - 1 >= second_packet_index:
                    first_packet = queue[first_packet_index]
                    second_packet = queue[second_packet_index]

                    is_ack_1 = struct.unpack('!B', first_packet[11:12])[0]
                    is_ack_2 = struct.unpack('!B', second_packet[11:12])[0]

                    if not first_packet_found:
                        if is_ack_1:
                            first_packet_index += 1
                        else:
                            first_packet_found = True

                    if (first_packet_found and not second_packet_found
                            and not is_ack_2):
                        second_packet_found = True
                        break

                    second_packet_index += 1  # if first packet increments,
                    # second packet has to as well

                if len(queue) - 1 >= second_packet_index:
                    queue[first_packet_index] = second_packet
                    queue[second_packet_index] = first_packet
                    print(f"first: {first_packet}, second: {second_packet}")
                    reorder_time = time.time()
    except KeyboardInterrupt:
        pass

def main():
    """Process command line arguments and call act_as_network"""
    # Define command line parameters.
    parser = argparse.ArgumentParser(
        prog='network_proxy', description='Simulates a network')
    parser.add_argument('-drop', action='store')
    parser.add_argument('-reorder', action='store')
    parser.add_argument('-corrupt', action='store')

    args = parser.parse_args()

    act_as_network(args)

if __name__ == '__main__':
    main()