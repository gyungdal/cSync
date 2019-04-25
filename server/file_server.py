import multiprocessing as mp
import logging
import socket
import time

logger = mp.log_to_stderr(logging.DEBUG)

def worker(socket):
    while True:
        client, address = socket.accept()
        logger.debug("{u} connected".format(u=address))
        client.send("OK")
        client.close()
if __name__ == '__main__':
    num_workers = 5

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('',9090))
    serversocket.listen(5)

    workers = [mp.Process(target=worker, args=(serversocket,)) for i in
            range(num_workers)]

    for p in workers:
        p.daemon = True
        p.start()

    while True:
        try:
            time.sleep(10)
        except:
            break