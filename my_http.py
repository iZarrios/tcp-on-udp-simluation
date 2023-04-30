import socket
from urllib.parse import parse_qs
# Set up a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set up the server address and port
server_address = ('localhost', 8080)
server_socket.bind(server_address)

# Start listening for incoming connections
server_socket.listen(1)
print('Server listening on {}:{}'.format(*server_address))

# Serve incoming connections
while True:
    # Accept a new connection
    client_socket, client_address = server_socket.accept()
    print('Received connection from {}:{}'.format(*client_address))

    # Read the client's request
    request = client_socket.recv(1024)
    print('Received request:\n{}'.format(request.decode()))

    # Parse the request method and data
    method, path, version = request.decode().split('\r\n')[0].split()
    data = request.decode().split('\r\n\r\n')[1]
    query_params = parse_qs(path.split('?')[1]) if '?' in path else {}
    param = query_params.get('name', ['World'])[0]

    # Generate the response based on the request
    if method == 'GET':
        if path == '/' or param:
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nHello, {param}!'.encode()
        elif path == '/form':
            response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<form method="POST" action="/post"><input type="text" name="name"><input type="submit"></form>'
        else:
            response = b'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n404 Not Found'
    elif method == 'POST':
        if path == '/post':
            name = data.split('=')[1].replace('+', ' ')
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nHello, {name}!'.encode()
        else:
            response = b'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n404 Not Found'
    else:
        response = b'HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n400 Bad Request'

    # Send the response back to the client
    client_socket.sendall(response)
    client_socket.close()

