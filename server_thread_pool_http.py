from socket import *
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
)

httpserver = HttpServer()


def ProcessTheClient(connection, address):
    logging.info(f"Processing client from {address}")
    rcv = b""
    try:
        while True:
            data = connection.recv(1024)
            if data:
                rcv += data
                # Check if we have received the full headers
                if b"\r\n\r\n" in rcv:
                    header_part, _, body_part = rcv.partition(b"\r\n\r\n")
                    decoded_header = header_part.decode()

                    content_len_str = [
                        h
                        for h in decoded_header.split("\r\n")
                        if h.lower().startswith("content-length:")
                    ]

                    if content_len_str:
                        content_len = int(content_len_str[0].split(":")[1].strip())
                        # Wait for the rest of the body if not fully received
                        while len(body_part) < content_len:
                            more_data = connection.recv(1024)
                            if not more_data:
                                break
                            rcv += more_data
                            body_part += more_data

                    # Once all data is received
                    hasil = httpserver.proses(rcv.decode(errors="ignore"))
                    connection.sendall(hasil)
                    break
            else:
                break
    except Exception as e:
        logging.error(f"Error processing client {address}: {e}")
    finally:
        logging.info(f"Connection from {address} closed.")
        connection.close()
    return


def Server():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind(("0.0.0.0", 8885))
    my_socket.listen(10)

    logging.info("Thread Pool Server running on port 8885")

    with ThreadPoolExecutor(max_workers=20, thread_name_prefix="Worker") as executor:
        while True:
            try:
                connection, client_address = my_socket.accept()
                logging.info(f"Accepted connection from {client_address}")
                executor.submit(ProcessTheClient, connection, client_address)
            except KeyboardInterrupt:
                logging.info("Server shutting down.")
                break
    my_socket.close()


if __name__ == "__main__":
    Server()
