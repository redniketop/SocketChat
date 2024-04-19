import socket  # Import the socket library for network connections
import threading  # Import the threading library to run parallel tasks

# Define the ChatClient class
class ChatClient:
    # Initialize the ChatClient with default host and port
    def __init__(self, host='localhost', port=50000):
        self.host = host  # Server's hostname or IP address
        self.port = port  # Port used by the server for connections
        # Create a TCP socket for the client
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True  # Flag to control the running state of threads

    # Connect to the server and handle message sending and receiving
    def connect_to_server(self):
        try:
            # Establish connection to the server
            self.client_socket.connect((self.host, self.port))
            print("Connected to server.")  # Inform user of successful connection
        except Exception as e:
            # Handle exceptions during connection attempt
            print(f"Failed to connect to server: {e}")
            return  # Exit function if connection fails

        # Create a thread to handle incoming messages from the server
        thread_receive = threading.Thread(target=self.receive_messages)
        thread_receive.start()  # Start the thread for receiving messages

        self.send_messages()  # Begin sending messages to the server

    # Listen for incoming messages and print them
    def receive_messages(self):
        while self.running:  # While the client is active
            try:
                # Receive a message from the server
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    # If no message is received, the server has disconnected
                    print("Disconnected from server.")
                    break  # Exit the loop and end the thread
                if "is prime" in message or "is not prime" in message:
                    # Identify prime computation results and print them
                    print(f"Prime Computation Result: {message}")
                else:
                    # Print regular messages
                    print(f"Message: {message}")
            except Exception as e:
                # Handle exceptions during message reception
                print(f"Error receiving message: {e}")
                break  # Exit the loop and end the thread

    # Send messages to the server as entered by the user
    def send_messages(self):
        try:
            while self.running:  # While the client is active
                # Get user input
                message = input('')
                if message.lower() == 'quit':  # If the user wants to quit
                    # Inform user of disconnection
                    print("Disconnecting from the server.")
                    self.running = False  # Set the running flag to False
                    break  # Break the loop to stop sending messages
                # Send the message to the server
                self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            # Handle exceptions during message sending
            print(f"Error sending message: {e}")
        finally:
            # Close the client socket when done
            self.client_socket.close()

# Define the main function to create and start the client
def main():
    # Create an instance of ChatClient
    chat_client = ChatClient('localhost', 50000)
    # Connect the client to the server
    chat_client.connect_to_server()

# Check if the script is the main program and run it
if __name__ == '__main__':
    main()
