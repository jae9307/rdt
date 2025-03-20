import argparse
import send_process

def main():
    # Define command line parameters.
    parser = argparse.ArgumentParser(
        prog='network_proxy', description='Simulates a network')
    parser.add_argument('filename')

    args = parser.parse_args()

    file = open(args.filename, "r")
    content = file.read().strip()
    file.close()

    send_process.rdt_sender_process(content)

if __name__ == '__main__':
    main()