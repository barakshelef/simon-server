import socket
import threading
import socketserver
from typing import Dict

HANDSHAKE_OK_MESSAGE = "OK"
STOP_SERVER_MESSAGE = "STOP_SERVER"
END_GAME_MESSAGE = "END_GAME"
SERVER_STOP_EVENT = threading.Event()


class Game:
    def __init__(self, game_id: int):
        self.id = game_id
        self._requests = []
        self._event = threading.Event()

    def register(self, request: socket.socket):
        player_id = len(self._requests)
        self._requests.append(request)
        return player_id

    def sendall(self, data: bytes):
        if not self._requests:
            return

        for request in self._requests:
            request.sendall(data)

    def has_ended(self):
        return self._event.is_set()

    def end(self):
        return self._event.set()


g_new_storage: Dict[int, Game] = {}


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        handshake_message = ''
        while not handshake_message:
            handshake_message = str(self.request.recv(1024), 'ascii')

        if handshake_message == STOP_SERVER_MESSAGE:
            print("Got STOP_SERVER_MESSAGE handshake")
            SERVER_STOP_EVENT.set()
            return

        game_id = int(handshake_message)
        if game_id not in g_new_storage:
            g_new_storage[game_id] = Game(game_id)

        self._game = g_new_storage[game_id]
        self._player_id = self._game.register(self.request)

        print(f"Registered game ID: {self._game.id} player #{self._player_id}")
        self.request.sendall(bytes(HANDSHAKE_OK_MESSAGE, 'ascii'))

        self.request.settimeout(1)

    def handle(self):
        while not SERVER_STOP_EVENT.is_set() and not self._game.has_ended():
            try:
                data = self.request.recv(1024)
            except socket.timeout:
                continue

            message = str(data, 'ascii')
            if message == END_GAME_MESSAGE:
                print(f"Player #{self._player_id} ended game {self._game.id}")
                self._game.end()
                return

            print(f"{self._game.id}#{self._player_id}: {message}")
            self._game.sendall(data)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        SERVER_STOP_EVENT.wait()

        print("Shutting down")
        server.shutdown()
