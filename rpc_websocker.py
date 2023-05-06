
import websocket
ws = websocket.WebSocket()
ws.connect("wss://www.blockonomics.co/payment/")
ws.send("{'addr': '189CEMECgP36iXpCKQoBbRQn3dTCUPi5dm'")
print(ws.recv())
ws.close()