from ParserHttp import HttpRequest, HttpResponse

req1="""GET /index.html HTTP/1.1\r\n
Host: www.example.com\r\n
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0\r\n
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n
Accept-Language: en-US,en;q=0.5\r\n
Accept-Encoding: gzip, deflate\r\n
Connection: keep-alive\r\n
\r\n"""



req2="""POST /users HTTP/1.1\r\n
Host: example.com\r\n
Content-Type: application/json\r\n
Content-Length: 56\r\n
Authorization: Bearer xxxxxxxx\r\n
\r\n"""


req3="""GET /index.html HTTP/1.1\r\n
Host: www.example.com\r\n
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0\r\n
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n
Accept-Language: en-US,en;q=0.5\r\n
Accept-Encoding: gzip, deflate\r\n
Connection: keep-alive\r\n
\r\n"""


response1="""
HTTP/1.1 200 OK\r\n
Content-Type: application/json; charset=UTF-8\r\n
Date: Fri, 30 Apr 2023 10:00:00 GMT\r\n
Expires: Fri, 30 Apr 2023 11:00:00 GMT\r\n
Cache-Control: public, max-age=3600\r\n
\r\n"""

response2="""
HTTP/1.1 200 OK\r\n
Date: Sun, 26 Sep 2010 20:09:20 GMT\r\n
Server: Apache/2.0.52 (CentOS)\r\n
Last-Modified: Tue, 30 Oct 2007 17:00:02 GMT\r\n
ETag: "17dc6-a5c-bf716880"\r\n
Accept-Ranges: bytes\r\n
Content-Length: 2652\r\n
Keep-Alive: timeout=10, max=100\r\n
Connection: Keep-Alive\r\n
Content-Type: text/html; charset=ISO-8859-1\r\n
\r\n
data data data data data """

response3="""
HTTP/1.1 200 OK\r\n
Content-Length: 55\r\n
Content-Type: text/html\r\n
Last-Modified: Wed, 12 Aug 1998 15:03:50 GMT\r\n
Accept-Ranges: bytes\r\n
ETag: “04f97692cbd1:377”\r\n
Date: Thu, 19 Jun 2008 19:29:07 GMT\r\n
\r\n"""


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


print("\n\nSTARTING OVER\n\n")
print(http_response)
