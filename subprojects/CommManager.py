import socket
import subprojects.misc.LowLevelFuncions as llw
import pickle
import io

logger = llw.script_logger('COMM MANAGER')


class CommManager:
    def __init__(self, config_rt):
        self.clients = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (config_rt.hostname, config_rt.port)
        self.client_connected = False

    def listen_incoming_connections(self):
        self.sock.bind(self.server_address)
        self.sock.settimeout(1)
        # Listen for incoming connections
        self.sock.listen(5)

    def accept_incoming_connections(self):
        for i in range(4 - len(self.clients)):
            try:
                connection, client_address = self.sock.accept()
                self.clients[connection] = client_address
                logger.info('New connection established: ' + str(client_address))
            except:
                pass

    def send_market_data_msg(self, data):
        buffer = pickle.dumps(data)
        logger.debug('Msg size: ' + str(len(buffer)))
        clients_list = list(self.clients.keys())
        msg_sent = False
        for client in clients_list:
            try:
                n_bytes = client.send(str(len(buffer)).encode() + b"\r")
                client.sendall(buffer)
                msg_sent = True
            except Exception as e:
                logger.info('Client ' + str(self.clients[client]) + ' disconnected')
                del self.clients[client]

        if msg_sent:
            logger.info('Data market message sent')

    def recv_market_data_msg(self):
        self.sock.settimeout(120.0)
        n_bytes = b""
        byte = None
        while byte != b"\r":
            byte = self.sock.recv(1)
            n_bytes += byte

        n_bytes = int(n_bytes)
        buffer = io.BytesIO()
        recibidos = 0
        while recibidos < n_bytes:
            msg = self.sock.recv(1024)
            buffer.write(msg)
            recibidos += len(msg)
        buffer.seek(0)
        data = pickle.loads(buffer.read())
        logger.info('Data server message received')
        return data

    def connect_with_server(self):
        logger.info('Connecting to {} port {}'.format(*self.server_address))
        try:
            self.sock.connect(self.server_address)
            self.client_connected = True
            logger.log(5, 'Connection with data server established')
        except Exception as e:
            logger.error(e)
