import sys
import ArducamDepthCamera as ac
import pickle 
import zmq
import time
import socket
import numpy as np

from multiprocessing import Process, Manager

MAX_DISTANCE = 4
port = 8090

def sender_task(queue):
 try:
  print("Start sender task")
  
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # get instance
    # look closely. The bind() function takes tuple as argument
  server_socket.bind(("", port))  # bind host address and port together

  while True:
    data = queue.get()
    #data = data.to_bytes(1, byteorder='big')
    print("got data ")
    if len(data) < 10:
      break
    # process the token received from a producer
    server_socket.sendto(data, ("192.168.0.10", 8099))
    print(f"{data[0]} sent")
    #queue.task_done()
 finally:
  print("closing socket")
  server_socket.close()


def test_task(queue):
  while True:
    print("put")
    time.sleep(1) 
    queue.put((1).to_bytes(1, byteorder='big'))
    

def camera_task(queue):
  try:
    cam = ac.ArducamCamera()
    #if cam.open(ac.TOFConnect.CSI,0) != 0 :
    #    print("initialization failed")
    #if cam.start(ac.TOFOutput.RAW) != 0 :
    #    print("Failed to start camera")
    if cam.open(ac.TOFConnect.CSI,0) != 0 :
        print("initialization failed")
    if cam.start(ac.TOFOutput.DEPTH) != 0 :
        print("Failed to start camera")
    cam.setControl(ac.TOFControl.RANG,MAX_DISTANCE)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind(("", port))  # bind host address and port together

    count = 0
 #   server_socket.listen(1)
 #   conn, address = server_socket.accept()  # accept new connection
 #   print("Connection from: " + str(address))
    while True:
        t1= round(time.time() * 1000)
        frame = cam.requestFrame(200)
        if frame != None:
            #buf = frame.getRawData()
            depth_buf = frame.getDepthData()
            amplitude_buf = frame.getAmplitudeData()
            amplitude_buf*=(255/1024)
            amplitude_buf = np.clip(amplitude_buf, 0, 255)

            #amplitude_buf = amplitude_buf / amplitude_buf.max() #normalizes data in range 0 - 255
            #amplitude_buf = 255 * amplitude_buf
            amplitude_buf = amplitude_buf.astype(np.uint8)
            print(amplitude_buf.size)
            t2 = round(time.time() * 1000)
            
            print(f"{depth_buf.shape} {depth_buf.dtype} {count}")           

            #obj = [depth_buf, amplitude_buf, count, round(time.time() * 1000)]
            #data = pickle.dumps(obj)
            #print(len(data))
            #socket.send(data)
            depth_buf = np.nan_to_num(depth_buf)
            depth_data = depth_buf.astype(np.float32).tobytes()
            data1 = amplitude_buf.tobytes()
            print(len(depth_data))
            frame_num = (count % 256).to_bytes(1, byteorder='big')
            chunks = [(x).to_bytes(1, byteorder='big') for x in [1, 2, 3, 4, 5]]
            step=43200
            data2 = depth_data[:step]
            data3 = depth_data[step:2 * step]
            data4 = depth_data[2 * step:3 * step]
            data5 = depth_data[3 * step:4 * step]
            data = [data1, data2, data3, data4, data5]
            for chunk, d in zip(chunks, data):
              #await asyncio.sleep(1)
              start_time = time.perf_counter()
              data = frame_num + chunk + d
              end_time = time.perf_counter()

              execution_time = (end_time - start_time) * 1e6  # Convert seconds to microseconds
              print("Concat time:", execution_time, "microseconds")
              start_time = time.perf_counter()
              server_socket.sendto(data, ("192.168.0.10", 8099))
              end_time = time.perf_counter()

              execution_time = (end_time - start_time) * 1e6  # Convert seconds to microseconds
              print("Send time:", execution_time, "microseconds")
              #queue.put(frame_num + chunk + d)
            cam.releaseFrame(frame)
            count += 1
            #if count > 100:
            #  queue.put((1).to_bytes(1, byteorder='big'))
            #  break
  finally:
    print("Finish")


def main():
  camera_task(None)
main()

