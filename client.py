import socket
import os


def list_files(server_address):
    """Sends a LIST request to the server."""
    with socket.create_connection(server_address) as sock:
        sock.sendall(b"LIST / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        response = sock.recv(4096).decode(errors="ignore")
        print("--- File List ---\n", response)


def upload_file(server_address, filename):
    """Uploads a local file to the server."""
    try:
        with open(filename, "rb") as f:
            content = f.read()

        request_header = (
            f"POST /{os.path.basename(filename)} HTTP/1.1\r\n"
            f"Host: localhost\r\n"
            f"Content-Length: {len(content)}\r\n\r\n"
        )

        request = request_header.encode() + content

        with socket.create_connection(server_address) as sock:
            sock.sendall(request)
            response = sock.recv(4096).decode(errors="ignore")
            print(f"--- Upload {filename} ---\n", response)

    except FileNotFoundError:
        print(f"Error: Local file '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred during upload: {e}")


def delete_file(server_address, filename):
    """Sends a DELETE request to the server."""
    request = f"DELETE /{filename} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode()
    with socket.create_connection(server_address) as sock:
        sock.sendall(request)
        response = sock.recv(4096).decode(errors="ignore")
        print(f"--- Delete {filename} ---\n", response)


if __name__ == "__main__":
    server_host = input("Enter server host (default: 172.18.0.4): ") or "172.18.0.4"
    server_port_input = input("Enter server port (default: 8889): ") or "8889"
    server_port = int(server_port_input)
    server_addr = (server_host, server_port)


    upload_filename = "upload_test.txt"
    with open(upload_filename, "w") as f:
        f.write("This is a test.")

    print(f"--- Testing Server on {server_addr} ---")

    print("\n1. Listing initial files:")
    list_files(server_addr)

    print(f"\n2. Uploading '{upload_filename}':")
    upload_file(server_addr, upload_filename)

    print("\n3. Listing files after upload:")
    list_files(server_addr)

    print(f"\n4. Deleting '{upload_filename}':")
    delete_file(server_addr, upload_filename)

    print("\n5. Listing files after deletion:")
    list_files(server_addr)

    os.remove(upload_filename)