import socket
import threading
import multiprocessing

# Function to check if a number is prime
def is_prime(n):
    if n <= 1:  # Prime numbers are greater than 1
        return False
    if n <= 3:  # 2 and 3 are prime numbers
        return True
    if n % 2 == 0 or n % 3 == 0:  # Discard multiples of 2 and 3
        return False
    i = 5
    while i * i <= n:  # Check for factors up to the square root of n
        if n % i == 0 or n % (i + 2) == 0:  # If divisible, not a prime
            return False
        i += 6  # Skip even numbers and multiples of 3
    return True  # If no factors found, number is prime

# Worker function to check for prime and broadcast result
def prime_worker(number, broadcast_func, sender_socket):
    # Check if the number is prime and create a result message
    result_message = f"{number} is prime." if is_prime(number) else f"{number} is not prime."
    # Use the broadcast function passed to send the result to all clients
    broadcast_func(result_message.encode(), sender_socket)

# Server class to manage connections and communications
class ChatServer:
    # Initialize the server with a host and a port
    def __init__(self, host='localhost', port=50000):
        self.clients = []  # List to keep track of connected clients
        self.host = host  # Server host address
        self.port = port  # Server port number
        # Create a socket object for the server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Option to reuse the socket address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the server socket to the given host and port
        self.server_socket.bind((self.host, self.port))
        # Listen for incoming connections
        self.server_socket.listen()
        # Print server start message
        print(f"Server started on {self.host}:{self.port}")

    # Handle individual client connections
    def handle_connection(self, client_socket):
        while True:
            try:
                # Receive a message from the client
                message = client_socket.recv(1024).decode().strip()
                # If an empty message is received, the client has disconnected
                if not message:
                    break

                # Split the received message into parts to analyze
                parts = message.split()
                # If the message is a prime number command, process it
                if len(parts) == 2 and parts[0] == 'prime':
                    try:
                        # Convert the second part to an integer
                        num = int(parts[1])
                        # Start a new process to handle the prime number checking
                        p = multiprocessing.Process(target=prime_worker, args=(num, self.broadcast, client_socket))
                        p.start()
                    except ValueError:
                        # If conversion fails, send an error message to the client
                        client_socket.send("Invalid number for prime check.".encode())
                else:
                    # If not a prime command, broadcast the message to other clients
                    self.broadcast(message.encode(), client_socket)

            except socket.error as e:
                # Print socket error message
                print(f"Socket error: {e}")
                break

        # Remove the client from the list and close the socket
        self.clients.remove(client_socket)
        client_socket.close()
        # Print client disconnection message
        print("Disconnected a client")

    # Method to broadcast messages to all clients except the sender
    def broadcast(self, message, sender_socket):
        for client in self.clients:
            # Ensure we do not send the message back to the sender
            if client != sender_socket:
                try:
                    # Send the message to the client
                    client.send(message)
                except socket.error as e:
                    # If sending fails, print an error message, close the client socket, and remove from the list
                    print(f"Error sending message: {e}")
                    client.close()
                    self.clients.remove(client)

    # Method to start the server and wait for connections
    def start_server(self):
        print('Server is running and waiting for connections')
        try:
            while True:
                # Accept a new connection
                client_socket, addr = self.server_socket.accept()
                # Print a message indicating a new connection
                print(f'New connection established from {addr}')
                # Add the new client socket to the list of clients
                self.clients.append(client_socket)
                # Start a new thread to handle communication with the new client
                thread = threading.Thread(target=self.handle_connection, args=(client_socket,))
                thread.start()
        finally:
            # Close the server socket when the server stops running
            self.server_socket.close()
            print("Server closed")

# Check if the script is being run directly and start the server
if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.start_server()
