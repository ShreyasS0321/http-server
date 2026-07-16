from dataclasses import dataclass


@dataclass(slots=True)
class Response:
    status: str = "200 OK"
    body: str = ""
    content_type: str = "text/html"

    def to_bytes(self) -> bytes:
        body_bytes = self.body.encode("latin-1")
        headers = f"HTTP/1.1 {self.status}\r\n"
        headers += f"Content-Type: {self.content_type}\r\n"
        headers += f"Content-Length: {len(body_bytes)}\r\n"
        headers += "Connection: close\r\n"
        headers += "\r\n"
        return headers.encode("latin-1") + body_bytes
