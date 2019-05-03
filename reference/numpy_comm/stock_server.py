import socketserver
import sys
from ipc_comm import *
import numpy as np
from io import BytesIO

class StockTrader:
    def __init__(self):
        pass

    def TestData(self):

        result = dict()
        result['head'] = np.array(["Open", "High", "Low", "Close"])
        result['data'] = np.random.rand(1,4)

        return result




class ReqHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)


    def handle(self):

        data_transferred = 0
        command= self.request.recv(CMD_BUF_SIZE)
        command = command.decode()
        print('[%s, %s] command: %s' % (self.client_address[0], self.client_address[1], command))

        data_to_send = []

        if command == 'TestData':
            # Send result
            f = BytesIO()
            # process & generate
            result = stock_trader.TestData()
            np.savez(f, **result)
            f.seek(0)
            self.request.sendall(f.read())
            f.close()


        else:
            print("Unknown Command")
            return





if __name__ == '__main__':

    # Setup Cybos connection
    stock_trader = StockTrader()
    # Setup IPC connection
    print("Start echo server")
    print("Ctrl+C to stop server")
    try:
        server = socketserver.TCPServer((SERVER_IP, PORT_NUM), ReqHandler)
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nStock Server Terminated...")
        del server

