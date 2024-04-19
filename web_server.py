from time import sleep
from random import randint
import socket

PORT = 8000

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(1)

print('Listening on port %s...' % PORT)

while True:    
    # Wait for client connections
    client_connection, client_address = server_socket.accept()

    # Get the client request
    request = client_connection.recv(1024).decode()
    print(request)

    headers = request.split('\n')
    top_header = headers[0].split()
    filename = top_header[1]

    try:
        # Read contents of html file
        file = open("pages" + filename, "rb")
        content = file.read()
        file.close()

        # For web pages, delay response by several seconds so that responses from the 
        # server are far slower than cached responses
        if filename.endswith(".html"):
            sleep(randint(3, 5))

        # Send HTTP response
        response = b'HTTP/1.1 200 OK\r\n\r\n' + content
        client_connection.sendall(response)
    except FileNotFoundError:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        client_connection.send(response.encode())
    finally:
        client_connection.close()

# Close socket
server_socket.close()