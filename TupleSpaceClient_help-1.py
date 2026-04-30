import socket
import sys
import os

def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.
    sock = None


    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        sock.connect((hostname, port))
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            cmd = parts[0]
            

            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            op = ""
            key = ""
            value = ""
            message = ""

            # Determine the operators and key values
            if cmd == "READ":
                if len(parts) < 2:
                    print(f"Invalid line (missing key): {line}")
                    continue
                op = "R"
                key = parts[1]
            elif cmd == "GET":
                if len(parts) < 2:
                    print(f"Invalid line (missing key): {line}")
                    continue
                op = "G"
                key = parts[1]
            elif cmd == "PUT":
                if len(parts) < 3:
                    print(f"Invalid line (missing key or value): {line}")
                    continue
                op = "P"
                key = parts[1]
                value = parts[2]
            else:
                print(f"Unknown command: {line}")
                continue

            # Length Check
            if len(key) > 999:
                print(f"Key too long: {line}")
                continue
            if op == "P":
                if len(value) > 999 or len(key) + 1 + len(value) > 970:
                    print(f"Key+value too long: {line}")
                    continue

            # Calculate the message length and construct the message
            if op == "P":
                msg_len = 7 + len(key) + len(value)
                message = f"{msg_len:03d} P {key} {value}"
            else:  # R or G
                msg_len = 6 + len(key)
                message = f"{msg_len:03d} {op} {key}"


            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.
            # Send Request
            sock.sendall(message.encode())

            # Receive Response: Read the 3-byte length first
            resp_prefix = sock.recv(3)
            if not resp_prefix:
                print("Server disconnected")
                break
            resp_length = int(resp_prefix.decode())

            # Continue reading the remaining part
            remaining = resp_length - 3
            resp_body = b""
            while len(resp_body) < remaining:
                chunk = sock.recv(remaining - len(resp_body))
                if not chunk:
                    break
                resp_body += chunk

            response = resp_body.decode().strip()



            print(f"{line}: {response}")

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # TASK 4: Close the socket when done (already called for you — explain why
        # finally: is the right place to do this even if an error occurs above).
        if sock:
            sock.close()

if __name__ == "__main__":
    main()