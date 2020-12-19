# Simon Relay Server
The Simon Relay Server. It relays.
## Protocol
### Register Client
To register your client connect to the server and send the Game ID:
```python
import socket

SERVER_ADDRESS = ("localhost", 9999)

s = socket.socket()
s.connect(SERVER_ADDRESS)

GAME_ID = 12345
s.send(bytes(str(GAME_ID), "ascii"))

if s.recv(1024) == b"OK":
    print("Connected!")
```
If you receive the `OK` message then registration was successful.

### Send and receive data
Once you have a registered client, any data you send will be relayed to all other clients registered to your Game ID.
And you shall receive every message sent by all other clients registered to your Game ID.

### End Game
Simply send the `END_GAME` message over your registered client socket.

### Stop Server
Create a new client and send the `STOP_SERVER` message when registering, stead of Game ID.