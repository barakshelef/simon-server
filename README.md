# Simon Relay Server
The Simon Relay Server. It relays.
## Protocol
### Register Client
Connect to a websocket with the path `http://{server}/{game_id}`

### User state
Once connected, and every time someone else connects or disconnects, you will receive a user state message:
```json
{
  "type": "users",
  "count": 5
} 
``` 
Indicating how many users are currently connected to your game.

### Send and receive data
Every message you will send the websocket will be relayed as is to the other clients