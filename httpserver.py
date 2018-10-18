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
    :author: Seth Fenske
    """
    header_dict, request_type = handle_header(request_socket)
    if(request_type == b'GET'):
        file_path = get_requested_file(header_dict)
        file_path = file_path[1: len(file_path)]

        if file_exists(file_path):
            file = open(file_path, 'rb')
            mime_type = get_mime_type(file_path)
            file_length = int(get_file_size(file_path))
            http_version = header_dict[b'version']

            packet_headers = get_packet_headers(mime_type, file_length, http_version)

            request_socket.send(packet_headers)
            request_socket.send(get_data_payload(file))
            request_socket.close()
        else:
            send404(request_socket)

    else:
        send505(request_socket)

def get_packet_headers(mime_type, file_length, http_version):
    """
    Takes the packet headers and formats them for sending.
    :param mime_type: Mime type of the resource
    :param file_length: Length of the resource
    :param http_version: HTTP version specified by get request
    :return: Vincent Zrenz
    """
    packet_headers = bytes(http_version) + b'HTTP/1.1 200 OK\r\n'
    packet_headers += b'Content-Length: ' + str(file_length).encode("ASCII") + b'\r\n'
    packet_headers += b'Content-Type: ' + bytes(mime_type.encode("ASCII")) + b'\r\n\r\n'
    return packet_headers

def handle_header(request_socket):
    """
    Reands the header and returns it as a dictionary
    :param request_socket: The socket to read from
    :return: Dictionary containing all the header information
    :author: Seth Fenske
    """
    header_dict = parse_header(request_socket)
    request_type = header_dict[b'request_type']
    return header_dict, request_type

def send505(request_socket):
    """
    Sends a hard-coded 505 response
    :param request_socket: Socket to send on
    :return: None
    :author: Seth Fenske
    """
    request_socket.send(b'HTTP/1.1 505 Operation Not Supported\r\n')
    request_socket.send(b'Content-Length: ' + str(20).encode("ASCII") + b'\r\n')
    request_socket.send(b'Content-Type: text/html\r\n\r\n')
    request_socket.send(b'<p>Not Supported</p>\r\n\r\n')

def send404(request_socket):
    """
    Send a hard-coded 404 response
    :param request_socket: Socket to send on
    :return: None
    :author: Seth Fenske
    """
    request_socket.send(b'HTTP/1.1 404 File Not Found\r\n')
    request_socket.send(b'Content-Length: ' + str(17).encode("ASCII") + b'\r\n')
    request_socket.send(b'Content-Type: text/html\r\n\r\n')
    request_socket.send(b'<p>Not Found</p>\r\n\r\n')

def parse_header(request_socket):
    """
    Reads the header into a dictionary
    :param request_socket: Socket to read from
    :return: The dictionary of headers
    :author: Vincent Krenz
    """
    header_dict = {}
    header_dict[b'request_type'] = read_until_space(request_socket)
    header_dict[b'request_message'] = read_until_space(request_socket)
    header_dict[b'version'] = read_until_CRLF(request_socket)

    header = read_until_CRLF(request_socket)
    while header != b'':
        header_dict[header.split(b': ')[0]] = header.split(b': ')[1]
        header = read_until_CRLF(request_socket)
    return header_dict

def get_requested_file(header_dict):
    """
    Gets the path of the requested file, returns index if nothing specified
    :param header_dict: Dictionary containing requested file
    :return: ASCII text of the file to be sent
    :author: Vincent Krenz
    """
    requested_file = header_dict[b'request_message']
    if requested_file == b'/':
        requested_file = b'/index.htm'
    return requested_file.decode("ASCII")

def get_data_payload(file):
    """
    Gets the payload from the message
    :param file: the file we are reading from
    :return: body
    :author: Vincent Krenz
    """
    body = file.read()
    body += b'\r\n\r\n'
    return body

def file_exists(file):
    """
    Checks that the file exists or throws an error
    :param file: file we are receiving from
    :return: boolean
    :rtype: boolean
    :author: Vincent Krenz
    """
    try:
        file = open(file, "r")
        return True
    except FileNotFoundError:
        print("File not found " + file)
        return False

def read_until_space(sock):
    """
    Reads until a space is found in the message
    :param sock: socket we are receiving the message from
    :return: message
    :rtype: bytes object
    :author: Seth Fenske
    """
    byte_0 = sock.recv(1)
    message = b''

    while(byte_0!=b' '):
        message += byte_0
        byte_0 = sock.recv(1)

    return message

def read_until_CRLF(sock):
    """
    Reads until a carriage return and a new line character, or an empty byte
    :param sock: socket we receive the file from
    :return: message
    :rtype: bytes object
    :author: Seth Fenske
    """
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
    :rtype: int or none
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

# The lab was extremely challenging. The excellent credit didn't quite seem fair. Why should a student do
# twice as much work for one extra point?