import time
from pathlib import Path
from socket import *

def fetch_file(filename):
    try: # Try to get file from the cache
        file = open("cache" + filename, "rb")
        file_from_cache = file.read()
        file.close()

        print("File " + filename + " fetched successfully from cache.")
        return file_from_cache
    except IOError: # Handle file not existing in cache
        print("File " + filename + " is not in cache. Fetching from server...")

        # Create socket and send a request to the web server
        socket_to_web_server = socket(AF_INET, SOCK_STREAM)
        socket_to_web_server.connect(('127.0.0.1', 8000))

        request = "GET " + filename + " HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        socket_to_web_server.send(request.encode())

        # Get response from the web server and get contents
        data = socket_to_web_server.recv(1024)
        response = b""

        while data:
            response += data
            data = socket_to_web_server.recv(1024)

        # Extract response header and data
        idx = response.find(b'\r\n\r\n')
        header = response[:idx]
        data = response[idx + 4:]
    
        # Close the socket to the web server
        socket_to_web_server.close()

        # Save file in cache
        if header.decode().startswith("HTTP/1.1 404 Not Found"):
           print("File not found.")
           return None
        else:
            print("Saving a copy of " + filename + " in the cache...")

            # Create necessary directories if they don't exist
            new_file = "cache" + filename
            new_file_dir = new_file[:new_file.rfind("/")] # Directory portion of filename
            Path(new_file_dir).mkdir(parents=True, exist_ok=True)

            file = open(new_file, 'wb+')
            file.write(data)
            file.close()

        return data

PORT = 8888

# Socket initialization
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(1)

print("Proxy server is listening on port " + str(PORT) + "...")

while 1:
    # Wait for client connection
    client_connection, client_address = server_socket.accept()

    # Get the client request
    request = client_connection.recv(1024).decode()
    print(request)

    # Parse HTTP headers and extract filename
    headers = request.split('\n')
    top_header = headers[0].split()

    if len(top_header) > 1:
        filename = top_header[1]

        # Index check
        if filename == "/":
            filename = "/index.html"
            
        response = ""

        try:
            # Get the file and start measuring the elapsed response time
            start_time = time.time()
            file_content = fetch_file(filename)
            elapsed = time.time() - start_time

            # Respond to client with file contents if found otherwise respond with error message
            if file_content:
                print("Retrieved web page in " + str(round(elapsed, 5)) + " seconds")
                response = b"HTTP/1.1 200 OK\r\n\r\n" + file_content
            else:
                response = "HTTP/1.1 404 NOT FOUND\r\n\r\n File Not Found".encode()
        except ConnectionRefusedError: # Error handling for when the web server is not running
            response = "HTTP/1.1 404 NOT FOUND\n\n Failed to communicate with web server".encode()
            print("Failed to communicate with web server.")

        client_connection.send(response)

    # Close the connection
    client_connection.close()
    print()

server_socket.close()