"""Read a file and send it using sender_process"""
import argparse
import send_process

def main():
    """
    opens a file and calls the sender process to send it
    """
    # Define command line parameters.
    parser = argparse.ArgumentParser(
        prog='client', description='Opens and sends a file')
    parser.add_argument('filename')

    args = parser.parse_args()

    file = open(args.filename, "r")
    content = file.read().strip()
    file.close()

    send_process.rdt_sender_process(content)

if __name__ == '__main__':
    main()