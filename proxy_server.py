import time
from socket import *

def fetch_file(filename):
    try: # Try to get file from the cache
        file = open("cache" + filename)
        file_from_cache = file.read()
        file.close()

        print("File " + filename + " fetched successfully from cache.")
        return file_from_cache
    except IOError: # Handle file not existing in cache
        print("File is not in cache. Fetching from server...")

        # Create socket and send a request to the web server

        # Get response from the web server and get contents

        # Close the socket to the web server

        # Save file in cache
        
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

    # Parse HTTP headers
    headers = request.split('\n')
    top_header = headers[0].split()
    filename = top_header[1]

    # Index check
    if filename == "/":
        filename = "/index.html"
        
    response = ""

    # Get the file and start measuring RTT
    start_time = time.time()
    content = fetch_file(filename)
    elapsed = time.time() - start_time

    # Respond to client with file contents if found otherwise respond with error message
    if content:
        response = "HTTP/1.1 200 OK\n\n" + content
        print("Retrieved web page in " + str(round(elapsed, 5)) + " seconds")
    else:
        response = "HTTP/1.1 404 NOT FOUND\n\n File Not Found"

    # Send the response and close the connection
    client_connection.send(response.encode())
    client_connection.close()
    print()

server_socket.close()