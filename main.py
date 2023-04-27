import os
import socket

# request_template = """\
# GET {path} HTTP/1.1\r
# Host: {host}\r
# User-Agent: {user_agent}\r
# Accept: {accept}\r
# Accept-Language: {accept_language}\r
# Accept-Encoding: {accept_encoding}\r
# Connection: {connection}\r
# \r
# """

HOST = 'localhost'
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
while True:
	# request = request_template.format(
	# 	path="/example.html",
	# 	host="www.example.com",
	# 	user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
	# 	accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	# 	accept_language="en-US,en;q=0.5",
	# 	accept_encoding="gzip, deflate, br",
	# 	connection="keep-alive"
	# )
	print(f'Server listening on {HOST}:{PORT}')
	conn, addr = s.accept()
	with conn:
		print(f'Connected by {addr}')
		request = conn.recv(1024)
		print(request)
		response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nHello World'
		conn.sendall(response)
