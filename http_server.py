import socket
import sys
import traceback

import os

import mimetypes

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """
    return b"\r\n".join([
        b'HTTP/1.1 200 OK',
        b'Content-Type: ' + mimetype,
        b'',
        body,
        ])

def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    return b"\r\n".join([
        b'HTTP/1.1 405 Method Not Allowed',
        b'',
        b'no can do buddy',
        ])


def response_not_found():

    return b"\r\n".join([
        b'HTTP/1.1 404 Not Found',
        b'',
        b'nothing here buddy',
        ])

def parse_request(request):

    method, path, version = request.split('\r\n')[0].split()

    if method != 'GET':
        raise NotImplementedError

    return path

def response_path(path):

    content = b""
    mime_type = b""

    mesa = []

    directory = os.path.abspath('webroot')
    lunch = directory + path

    if os.path.isdir(lunch):  # is True:
        for root, dirs, files in os.walk(lunch):  
        # this doesn't display the 'images' directory within 'webroot' directory
            for filename in files:
                mesa += [(' \n' + filename).encode('utf8')]
            for dirname in dirs:
                mesa += [(' \n' + dirname).encode('utf8')]
        # EDIT, now it does

        # mime_type = b"text/plain"
        mime_type = str(mimetypes.guess_type(path)[0]).encode('utf8')
        
        content = content.join(mesa)
        return content, mime_type

    if os.path.isfile(lunch):
        mime_type = str(mimetypes.guess_type(path)[0]).encode('utf8')
        with open(lunch, 'rb') as f:
            content = f.read()
        return content, mime_type

    raise NameError


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10069)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break
		
                print("Request received:\n{}\n\n".format(request))

                try:
                    path = parse_request(request)

                    content, mime_type = response_path(path)

                    response = response_ok(
                        body=content,
                        mimetype=mime_type
                    )

                except NotImplementedError:
                    response = response_method_not_allowed()
                    
                except NameError:
                    response = response_not_found()

                conn.sendall(response)

            except:
                traceback.print_exc()
            finally:
                conn.close() 

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)


