import asyncio
from typing import Callable

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Input, Label, ListItem, ListView


class Client:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    async def connect(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def send(self, data: str) -> None:
        self.writer.write(data.encode())
        await self.writer.drain()

    async def recv(self, cb: Callable[[str], None]) -> None:
        while True:
            data = await self.reader.read(1024)
            cb(data.decode())


class Chat(App):
    CSS_PATH = "style.tcss"

    def __init__(self, client: Client) -> None:
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        yield ListView()
        yield Input(placeholder="Message...")

    async def on_mount(self) -> None:
        await self.client.connect()
        asyncio.get_running_loop().create_task(self.client.recv(self.add_message))

    def add_message(self, message: str) -> None:
        self.query_one(ListView).append(ListItem(Label(message)))

    @on(Input.Submitted)
    async def on_submit(self, event: Input.Submitted) -> None:
        self.add_message(event.value)
        await self.client.send(event.value)
        event.input.clear()


if __name__ == "__main__":
    app = Chat(Client("127.0.0.1", 5000))
    app.run()
