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

    sock, message = create_request(host, port, resource)
 
    return 500  # Replace this "server error" with the actual status code

def create_request(host, port, resource):
    """
        Takes the arguments, and creates a TCP connection which points
      to the specified item. It also then creates a byte object representing the ASCII request.
      Both of these are then returned.
    :param host:
    :param port:
    :param resource:
    :return: (tcp_socket, request_bytestring)
    :rtype: socket and bytestring
    :author: Seth Fenske
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    message = b'GET ' + resource + b' HTTP/1.1' + b'\x0D\x0A' + b'Host: msoe.us\r\nConnection: keep-alive\r\n\r\n'

    sock.sendall(message)
    recieve_request(sock, message)

    return sock, message


def recieve_request(tcp_socket, request_bytestring):
    """
    Uses the socket and bytestring to open the connection
    to the server and listens for a response. It then returns the response from the server.
    :param tcp_socket:
    :param request_bytestring:
    :return: (server response)
    :rtype: byte object
    :author: Vincent Krenz
    """

    divide_response(tcp_socket)

def divide_response(sock):
    """
    Takes the entire response and looks for where the header terminates.
    It simply returns a tuple. First element is a string representing the header response.
    The second item is the byte object representing the payload.
    :param response_bytes:
    :return (header, body)
    :author: Seth Fenske
    """
    httpVersion = scan_until_space(sock)
    httpStatusCode = scan_until_space(sock)
    httpCodeMessage = scan_until_space(sock)

    print(httpVersion.decode("ASCII") + ":::" + httpStatusCode.decode("ASCII") + " ::: " + httpCodeMessage.decode("ASCII"))




def scan_until_space(sock):
    lastByte = sock.recv(1)
    message = b''

    while (lastByte != b' '):
        message = message + lastByte
        lastByte = sock.recv(1)

    return message

def get_after_header(sock):
    first_byte = sock.recv(1)
    second_byte = sock.recv(1)
    third_byte = sock.recv(1)
    fourth_byte = sock.recv(1)

    while(first_byte != b'\r' and second_byte != '\n' and third_byte !=b'\r' and fourth_byte != b'\n'):
        fourth_byte = third_byte
        third_byte = second_byte
        second_byte = first_byte
        first_byte = sock.recv(1)

    #Now we reached the end of the header
    data = b''

    while (first_byte != b'\r' and second_byte != '\n' and third_byte != b'\r' and fourth_byte != b'\n'):
        fourth_byte = third_byte
        third_byte = second_byte
        second_byte = first_byte
        first_byte = sock.recv(1)
        if(first_byte != b'\r' and second_byte != '\n' and third_byte != b'\r' and fourth_byte != b'\n'):
            data = data + fourth_byte




def status_code(header):
    """
    Finds and returns the status code of the http response
    :param header:
    :return: status code
    :rtype: int
    :author: Vincent Krenz
    """
main()
