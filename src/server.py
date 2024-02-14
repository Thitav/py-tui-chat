import asyncio
from asyncio import StreamReader, StreamWriter


class Server:
    clients_counter = 0
    clients: dict[int, StreamWriter] = {}

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    async def serve(self) -> None:
        srv = await asyncio.start_server(self.handle_client, self.host, self.port)
        await srv.serve_forever()

    async def handle_client(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.clients_counter += 1
        client_id = self.clients_counter
        self.clients[client_id] = writer

        while True:
            data = await reader.read(1024)
            if not data:
                del self.clients[client_id]
                break

            for cid in self.clients:
                if not cid == client_id:
                    self.clients[cid].write(data)
                    await writer.drain()


server = Server("127.0.0.1", 5000)
asyncio.run(server.serve())
