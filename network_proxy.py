import socket

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
    server_port = 67   # arbitrary number

    packet = recieve(address, network_proxy_port)

    # TODO: mess up packet in some way

    # TODO: check who is sending the packet, act accordingly

    forward(packet, address, server_port)

def main():
    act_as_network()

if __name__ == '__main__':
    main()