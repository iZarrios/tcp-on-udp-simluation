# HTTP request string
request_str = "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n"

# Parse the HTTP request
request_lines = request_str.split("\r\n")
request_line = request_lines[0].split()
method = request_line[0]
url = request_line[1]
http_version = request_line[2].split("/")[1]

headers = {}
for header_line in request_lines[1:]:
    if header_line:
        if ":" in header_line:
            key, value = header_line.split(": ")
            headers[key] = value
        else:
            print(f"Invalid header line: {header_line}")

# HTTP response string
response_str = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: 123\r\n\r\n<html><body>Hello, world!</body></html>"

# Parse the HTTP response
response_lines = response_str.split("\r\n")
response_line = response_lines[0].split()
http_version = response_line[0]
status_code = int(response_line[1])
reason_phrase = " ".join(response_line[2:])

headers = {}
for header_line in response_lines[1:]:
    if header_line:
        if ":" in header_line:
            key, value = header_line.split(": ")
            headers[key] = value
        else:
            print(f"Invalid header line: {header_line}")

body = "\r\n".join(response_lines[response_lines.index("")+1:])

# Print the parsed request and response
print("Request:")
print(f"Method: {method}")
print(f"URL: {url}")
print(f"HTTP Version: {http_version}")
print("Headers:")
for key, value in headers.items():
    print(f"{key}: {value}")

print("\nResponse:")
print(f"HTTP Version: {http_version}")
print(f"Status Code: {status_code}")
print(f"Reason Phrase: {reason_phrase}")
print("Headers:")
for key, value in headers.items():
    print(f"{key}: {value}")
print(f"Body: {body}")
