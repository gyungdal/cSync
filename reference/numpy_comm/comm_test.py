import socket
import sys
import ipc_comm as comm
import numpy as np
from io import BytesIO


def send_command(message):

  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    try:
      server_address = (comm.SERVER_IP, comm.PORT_NUM)
      sock.connect(server_address)

      # req_test
      encoded_message = message.encode()
      sock.sendall(encoded_message)

      file_buffer = b''
      while True:
        receiving_buffer = sock.recv(comm.BUF_SIZE)
        if not receiving_buffer:
          break
        file_buffer += receiving_buffer

      if len(file_buffer) == 0:
        return None

      final_image = np.load(BytesIO(file_buffer))

    except Exception as e:
      print(e)
      return None, None

  if len(final_image.files) > 0:
    return (final_image[file_name] for file_name in final_image.files)
  else:
    return None, None


if __name__ == '__main__':

  head, data = send_command("TestData")
  print("Head:", head)
  print("Data:", data)

  print("K-Scalper Terminated.")
