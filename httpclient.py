r"""
- CS2911 - 011
- Fall 2017
- Lab 5
- Names: Vincent Krenz, Seth Fenske
  - 
  - 

A simple HTTP client
"""

# import the "socket" module -- not using "from socket import *" in order to selectively use items with "socket." prefix
import socket

# import the "regular expressions" module
import re


def main():
    """
    Tests the client on a variety of resources
    """

    # These resource request should result in "Content-Length" data transfer
    get_http_resource('http://msoe.us/taylor/images/taylor.jpg','taylor.jpg')

    # this resource request should result in "chunked" data transfer
    get_http_resource('http://msoe.us/taylor/','index.html')
    
    # If you find fun examples of chunked or Content-Length pages, please share them with us!



def get_http_resource(url, file_name):
    """
    Get an HTTP resource from a server
           Parse the URL and call function to actually make the request.

    :param url: full URL of the resource to get
    :param file_name: name of file in which to store the retrieved resource

    (do not modify this function)
    """

    # Parse the URL into its component parts using a regular expression.
    url_match = re.search('http://([^/:]*)(:\d*)?(/.*)', url)
    url_match_groups = url_match.groups() if url_match else []
    #    print 'url_match_groups=',url_match_groups
    if len(url_match_groups) == 3:
        host_name = url_match_groups[0]
        host_port = int(url_match_groups[1][1:]) if url_match_groups[1] else 80
        host_resource = url_match_groups[2]
        print('host name = {0}, port = {1}, resource = {2}'.format(host_name, host_port, host_resource))
        status_string = make_http_request(host_name.encode(), host_port, host_resource.encode(), file_name)
        print('get_http_resource: URL="{0}", status="{1}"'.format(url, status_string))
    else:
        print('get_http_resource: URL parse failed, request not sent')


def write_binary_file(data, file_name):
    with open(file_name, "wb") as file:
        file.write(data)

def make_http_request(host, port, resource, file_name):
    """
    Get an HTTP resource from a server

    :param bytes host: the ASCII domain name or IP address of the server machine (i.e., host) to connect to
    :param int port: port number to connect to on server host
    :param bytes resource: the ASCII path/name of resource to get. This is everything in the URL after the domain name,
           including the first /.
    :param file_name: string (str) containing name of file in which to store the retrieved resource
    :return: the status code
    :rtype: int
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    message = b'GET ' + resource + b' HTTP/1.1' + b'\x0D\x0A' + b'Host: msoe.us\r\nConnection: keep-alive\r\n\r\n'

    sock.sendall(message)
    response, data = recieve_request(sock)

    write_binary_file(data, file_name)

    return response  # Replace this "server error" with the actual status code


def recieve_request(tcp_socket):
    """
    Uses the socket and bytestring to open the connection
    to the server and listens for a response. It then returns the response from the server.
    :param tcp_socket:
    :return: (server response)
    :rtype: byte object
    :author: Vincent Krenz
    """
    status_code, data = divide_response(tcp_socket)
    return status_code, data


def get_by_length(sock, content_length):
    body = b''
    for i in range(0, content_length):
        body+=sock.recv(1)

    return body


def get_by_chunking(sock):
    data = b''
    length = read_socket_until_newline(sock)

    while length != b'':
        data += get_chunk(sock, int(str(length.decode()), 16))
        print(data.decode("ASCII"))
        length = read_socket_until_newline(sock)

    return data


def get_chunk(sock, length):
    data = b''
    for i in range(0, length):
        data += sock.recv(1)
    return data

def divide_response(sock):
    """
    Takes the entire response and looks for where the header terminates.
    It simply returns a tuple. First element is a string representing the header response.
    The second item is the byte object representing the payload.
    :param response_bytes:
    :return (header, body)
    :author: Seth Fenske
    """
    header_bytes = get_header_bytes(sock)
    response_code, data_by_chunking, content_length = parse_header(header_bytes)

    if data_by_chunking and content_length == 0:
        data = get_by_chunking(sock)
    else:
        data = get_by_length(sock, content_length)
        print("Length: " + str(content_length))

    return response_code, data


def get_header_bytes(sock):
    byte_4 = sock.recv(1)
    byte_3 = sock.recv(1)
    byte_2 = sock.recv(1)
    byte_1 = sock.recv(1)
    message = b''

    while not(byte_1 == b'\n' and byte_2 == b'\r' and byte_3 == b'\n' and byte_4 == b'\r'):
        message += byte_4
        byte_4 = byte_3
        byte_3 = byte_2
        byte_2 = byte_1
        byte_1 = sock.recv(1)

    return message


def scan_until_space(sock):
    lastByte = sock.recv(1)
    message = b''

    while (lastByte != b' '):
        message = message + lastByte
        lastByte = sock.recv(1)

    return message

def parse_header(header_bytes):
    header_dict = {}
    position = 0

    version, rep_code, response_text, position = read_header_bytes(header_bytes, position)
    header_dict, position = fill_dictionary(header_bytes, header_dict, position)

    data_by_chunking = False
    content_length = 0

    if b'Content-Length:' in header_dict:
        content_length = int(header_dict[b'Content-Length:'])
    else:
        if b'Transfer-Encoding:' in header_dict:
            data_by_chunking = True

    return rep_code, data_by_chunking, content_length

def fill_dictionary(header_bytes, header_dict, position):
    while header_bytes[position: position+4]!= b'':
        position, dict = add_key_val_pair(header_bytes, header_dict, position)
    return dict, position

def add_key_val_pair(bytes, dictionary, position):
    key, position = read_bytes_until_space(bytes, position)
    value, position = read_bytes_until_newline_return(bytes, position)
    dictionary[key] = value
    return position, dictionary


def read_header_bytes(header_bytes, position):
    version, position = read_bytes_until_space(header_bytes, position)
    code, position = read_bytes_until_space(header_bytes, position)
    description, position = read_bytes_until_newline_return(header_bytes, position)
    return version, code, description, position


def read_bytes_until_space(header_bytes, position):
    lastByte = header_bytes[position: position+1]
    message = b''
    while (lastByte != b'\x20'):
        message += lastByte
        position += 1
        lastByte = header_bytes[position: position+1]
    position += 1
    return message, position

def read_socket_until_newline(sock):
    last_byte = sock.recv(1)
    current_byte = sock.recv(1)
    data = b''

    while(not(last_byte==b'\r' and current_byte==b'\n')):
        data += last_byte
        last_byte = current_byte
        current_byte = sock.recv(1)
    return data

def read_bytes_until_newline_return(header_bytes, position):
    lastByte = header_bytes[position: position+1]
    position += 1
    current_byte = header_bytes[position: position+1]
    message = b''
    while not(lastByte == b'\r' and current_byte==b'\n' or current_byte==b''):
        message = message + lastByte
        position += 1
        lastByte = current_byte
        current_byte = header_bytes[position: position+1]
    position += 1
    return message, position


main()
