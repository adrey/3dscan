import sys
import ArducamDepthCamera as ac
import pickle 
import zmq
import time
import socket


MAX_DISTANCE = 4
port = 8090
if __name__ == "__main__":
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    # look closely. The bind() function takes tuple as argument
  server_socket.bind(("", port))  # bind host address and port together

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

    count = 0
    server_socket.listen(1)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    while True:
        t1= round(time.time() * 1000)
        frame = cam.requestFrame(200)
        if frame != None:
            #buf = frame.getRawData()
            depth_buf = frame.getDepthData()
            amplitude_buf = frame.getAmplitudeData()
            print(amplitude_buf)
            t2 = round(time.time() * 1000)
            
            print(f"{depth_buf.shape} {depth_buf.dtype} {t2 - t1}")           

            #obj = [depth_buf, amplitude_buf, count, round(time.time() * 1000)]
            #data = pickle.dumps(obj)
            #print(len(data))
            #socket.send(data)
            data = amplitude_buf.tobytes()
            print(len(data))
            conn.send(data)
            cam.releaseFrame(frame)
            count += 1
  finally:
    print("closing socket")
    server_socket.close()
