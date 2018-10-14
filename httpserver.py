"""
- CS2911 - 0NN
- Fall 2017
- Lab N
- Names: Seth Fenske(fenskesd), Vincent Krenz (krenzva)
  - 
  - 

A simple HTTP server
"""

import socket
import re
import threading
import os
import mimetypes
import datetime


def main():
    """ Start the server """
    http_server_setup(8080)


def http_server_setup(port):
    """
    Start the HTTP server
    - Open the listening socket
    - Accept connections and spawn processes to handle requests

    :param port: listening port number
    """

    num_connections = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_address = ('', port)
    server_socket.bind(listen_address)
    server_socket.listen(num_connections)
    try:
        while True:
            request_socket, request_address = server_socket.accept()
            print('connection from {0} {1}'.format(request_address[0], request_address[1]))
            # Create a new thread, and set up the handle_request method and its argument (in a tuple)
            request_handler = threading.Thread(target=handle_request, args=(request_socket,))
            # Start the request handler thread.
            request_handler.start()
            # Just for information, display the running threads (including this main one)
            print('threads: ', threading.enumerate())
    # Set up so a Ctrl-C should terminate the server; this may have some problems on Windows
    except KeyboardInterrupt:
        print("HTTP server exiting . . .")
        print('threads: ', threading.enumerate())
        server_socket.close()


def handle_request(request_socket):
    """
    Handle a single HTTP request, running on a newly started thread.

    Closes request socket after sending response.

    Should include a response header indicating NO persistent connection

    :param request_socket: socket representing TCP connection from the HTTP client_socket
    :return: None
    """
    request_type = read_until_space(request_socket)
    status_code = b''
    if(request_type == b'GET'):

        requested_file = read_until_space(request_socket)

        print(requested_file)

        if requested_file==b'/':
            requested_file = b'/index.htm'

        file_path = requested_file.decode("ASCII")
        file_path = file_path[1: len(file_path)]

        print('File path ' + file_path)

        if file_exists(file_path):
            file = open(file_path, 'rb')
            mime_type = get_mime_type(file_path)
            file_length = int(get_file_size(file_path))
            http_version = read_until_CRLF(request_socket)
            data_payload = get_data_payload(file)

            packet_headers = bytes(http_version) + b' 200 OK\r\n'
            packet_headers += b'Content-Length: ' + str(file_length).encode("ASCII") + b'\r\n'
            #packet_headers += b'Content-Length: ' + b' 0'
            packet_headers += b'Content-Type: ' + bytes(mime_type.encode("ASCII")) + b'\r\n\r\n'

            print(packet_headers)

            request_socket.sendall(packet_headers + data_payload)
            request_socket.close()

        else:
              print("Not found " + file_path)
              status_code = b'404'

        status_code = b'200'
    else:
        status_code = b'404'

def get_data_payload(file):
    body = file.read()
    body += b'\r\n\r\n'
    return body

def file_exists(file):
    try:
        file = open(file, "r")
        return True
    except FileNotFoundError:
        print('FOund in')
        return False

def read_until_space(sock):
    byte_0 = sock.recv(1)
    message = b''

    while(byte_0!=b' '):
        message += byte_0
        byte_0 = sock.recv(1)

    return message

def read_until_CRLF(sock):
    last_byte = sock.recv(1)
    current_byte = sock.recv(1)

    message = b''

    while not(last_byte == b'\r' and current_byte == b'\n' or current_byte==b''):
        message += last_byte
        last_byte = current_byte
        current_byte = sock.recv(1)
    return message

# ** Do not modify code below this line.  You should add additional helper methods above this line.

# Utility functions
# You may use these functions to simplify your code.


def get_mime_type(file_path):
    """
    Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If successful in guessing the MIME type, a string representing the content type, such as 'text/html'
             Otherwise, None
    :rtype: int or None
    """

    mime_type_and_encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type_and_encoding[0]
    return mime_type


def get_file_size(file_path):
    """
    Try to get the size of a file (resource) as number of bytes, given its path

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If file_path designates a normal file, an integer value representing the the file size in bytes
             Otherwise (no such file, or path is not a file), None
    :rtype: int or None
    """

    # Initially, assume file does not exist
    file_size = None
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    return file_size


main()

# Replace this line with your comments on the lab
