import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
import logging


class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {}
        self.types[".pdf"] = "application/pdf"
        self.types[".jpg"] = "image/jpeg"
        self.types[".txt"] = "text/plain"
        self.types[".html"] = "text/html"

    def response(self, kode=404, message="Not Found", messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime("%c")
        resp = []
        resp.append(f"HTTP/1.1 {kode} {message}\r\n")
        resp.append(f"Date: {tanggal}\r\n")
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append(f"Content-Length: {len(messagebody)}\r\n")
        for kk in headers:
            resp.append(f"{kk}: {headers[kk]}\r\n")
        resp.append("\r\n")

        response_headers = "".join(resp)

        if not isinstance(messagebody, bytes):
            messagebody = messagebody.encode()

        return response_headers.encode() + messagebody

    def proses(self, data):
        # Log the first line of the request
        logging.info(f"Request received: {data.splitlines()[0]}")

        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n]
        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if method == "GET":
                return self.http_get(object_address, all_headers)
            elif method == "POST":
                body_start_index = data.find("\r\n\r\n") + 4
                body = data[body_start_index:]
                return self.http_post(object_address, all_headers, body)
            elif method == "LIST":
                return self.http_list(object_address, all_headers)
            elif method == "DELETE":
                return self.http_delete(object_address, all_headers)
            else:
                logging.warning(f"Unsupported method: {method}")
                return self.response(400, "Bad Request", "Unsupported method", {})
        except IndexError:
            logging.error("Malformed request received")
            return self.response(400, "Bad Request", "Malformed request", {})

    def http_get(self, object_address, headers):
        thedir = "."
        if object_address == "/":
            return self.response(200, "OK", "This is a test web server.", {})

        filepath = os.path.join(thedir, object_address.strip("/"))

        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, "rb") as fp:
                isi = fp.read()
            fext = os.path.splitext(filepath)[1]
            content_type = self.types.get(fext, "application/octet-stream")
            headers = {"Content-Type": content_type}
            return self.response(200, "OK", isi, headers)
        else:
            return self.response(404, "Not Found", "File not found.", {})

    def http_post(self, object_address, headers, body):
        filepath = os.path.join(".", object_address.strip("/"))
        try:
            with open(filepath, "wb") as f:
                if not isinstance(body, bytes):
                    body = body.encode()
                f.write(body)
            logging.info(f"File '{os.path.basename(filepath)}' uploaded successfully.")
            return self.response(
                201, "Created", f"File {os.path.basename(filepath)} uploaded.", {}
            )
        except Exception as e:
            logging.error(f"Error uploading file: {e}")
            return self.response(500, "Internal Server Error", str(e), {})

    def http_list(self, object_address, headers):
        try:
            items = os.listdir(".")
            message_body = "\n".join(items)
            headers = {"Content-Type": "text/plain"}
            return self.response(200, "OK", message_body, headers)
        except Exception as e:
            logging.error(f"Error listing directory: {e}")
            return self.response(500, "Internal Server Error", str(e), {})

    def http_delete(self, object_address, headers):
        filepath = os.path.join(".", object_address.strip("/"))
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                os.remove(filepath)
                logging.info(
                    f"File '{os.path.basename(filepath)}' deleted successfully."
                )
                return self.response(
                    200, "OK", f"File {os.path.basename(filepath)} deleted.", {}
                )
            except Exception as e:
                logging.error(f"Error deleting file: {e}")
                return self.response(500, "Internal Server Error", str(e), {})
        else:
            return self.response(404, "Not Found", "File not found.", {})
