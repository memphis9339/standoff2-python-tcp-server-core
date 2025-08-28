import socket
import threading
import structures_pb2

def send_message(sock, body):
    header = len(body).to_bytes(4, byteorder='big')
    sock.send(header + body)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"server listening on {self.host}:{self.port}")

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"somebody connected: {addr}!!!")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        try:
            while True:
                header = client_socket.recv(4)
                if not header:
                    break
                data_length = int.from_bytes(header, byteorder='big')
                if data_length != 1:
                    data = client_socket.recv(data_length)
                    request = structures_pb2.RpcRequest()
                    request.ParseFromString(data)
                    print(f"received RpcRequest: {request.service_name}.{request.method_name}, length: {data_length}")
                    if request.service_name == "TestAuthRemoteService":
                        if request.method_name == "auth":
                            result = auth(request.id)
                            send_message(client_socket, result)
                            print("test auth handled")
                else:
                    print("ping received, sending pong!")
                    client_socket.send((1).to_bytes(4, byteorder='big') + bytes([0x01]))

        except Exception as e:
            print(f"err {e}(")
        finally:
            pass

#testauthremote service.auth(), you can add other handlers for other services and methods
def auth(rpcId):
    response = structures_pb2.RpcResponse()
    response.id = rpcId
    token = structures_pb2.String()
    token.msg = "sometoken"

    response.returns.one = token.SerializeToString()
    responsemsg = structures_pb2.ResponseMessage()
    responsemsg.response.CopyFrom(response)
    serialized_response = responsemsg.SerializeToString()
    return serialized_response

if __name__ == "__main__":
    server = Server("0.0.0.0", 2222)

    server.start()
