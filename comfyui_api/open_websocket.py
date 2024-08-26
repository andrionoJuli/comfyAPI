import uuid
import websocket


def open_websocket_connection():
    """
      Establishes a websocket connection to ComfyUI running under the given address and returns the connection object, server address, and a unique client ID.

      Returns:
        tuple: A tuple containing the websocket connection object, server address (str), and client ID (str).
      """
    server_address = '127.0.0.1:8188'
    client_id = str(uuid.uuid4())
    ws = websocket.WebSocket()
    ws.connect('ws://{}/ws?clientId={}'.format(server_address, client_id))
    return ws, server_address, client_id