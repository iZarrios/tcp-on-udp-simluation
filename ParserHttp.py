class HttpRequest:
    def __init__(self, request_str):
        self.method = ""
        self.url = ""
        self.http_version = ""
        self.headers = {}

        # Parse the HTTP request
        request_lines = request_str.split("\r\n")
        request_line = request_lines[0].split()
        self.method = request_line[0]
        self.url = request_line[1]
        self.http_version = request_line[2].split("/")[1]

        for header_line in request_lines[1:]:
            if header_line:
                if ":" in header_line:
                    key, value = header_line.split(": ")
                    self.headers[key] = value

    def __str__(self):
        headers_str = "\r\n".join([f"{key}: {value}" for key, value in self.headers.items()])
        return f"{self.method} {self.url} HTTP/{self.http_version}\r\n{headers_str}\r\n"

class HttpResponse:
    def __init__(self, response_str):
        self.http_version = ""
        self.status_code = 0
        self.reason_phrase = ""
        self.headers = {}
        self.body = ""

        # Parse the HTTP response
        response_lines = response_str.split("\r\n")
        first_line = response_lines[0].split()
        self.http_version = first_line[0]
        self.status_code = int(first_line[1])
        self.reason_phrase = " ".join(first_line[2:])

        for header_line in response_lines[1:]:
            if header_line:
                if ":" in header_line:
                    key, value = header_line.split(": ")
                    self.headers[key] = value

        self.body = "\r\n".join(response_lines[response_lines.index("")+1:])

    def __str__(self):
        headers_str = "\r\n".join([f"{key}: {value}" for key, value in self.headers.items()])
        return f"HTTP/{self.http_version} {self.status_code} {self.reason_phrase}\r\n{headers_str}\r\n\r\n{self.body}"

# Example usage
request_str = "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n"
response_str = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: 123\r\n\r\n<html><body>Hello, world!</body></html>"

http_request = HttpRequest(request_str)
http_response = HttpResponse(response_str)

print("Request:")
print(f"Method: {http_request.method}")
print(f"URL: {http_request.url}")
print(f"HTTP Version: {http_request.http_version}")
print("Headers:")
for key, value in http_request.headers.items():
    print(f"{key}: {value}")

print("\nResponse:")
print(f"HTTP Version: {http_response.http_version}")
print(f"Status Code: {http_response.status_code}")
print(f"Reason Phrase: {http_response.reason_phrase}")
print("Headers:")
for key, value in http_response.headers.items():
    print(f"{key}: {value}")
print(f"Body: {http_response.body}")
