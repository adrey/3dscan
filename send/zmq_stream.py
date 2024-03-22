import sys
import ArducamDepthCamera as ac
import pickle 
import zmq
import time

MAX_DISTANCE = 4
port = 8090
if __name__ == "__main__":
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

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    #socket.setsockopt(zmq.SNDHWM, 1)
    socket.bind("tcp://*:%s" % port)


    count = 0
    while True:
        t1= round(time.time() * 1000)
        frame = cam.requestFrame(200)
        if frame != None:
            #buf = frame.getRawData()
            depth_buf = frame.getDepthData()
            amplitude_buf = frame.getAmplitudeData()
            t2 = round(time.time() * 1000)
            
            print(f"{depth_buf.shape} {depth_buf.dtype} {t2 - t1}")           

            obj = [depth_buf, amplitude_buf, count, round(time.time() * 1000)]
            data = pickle.dumps(obj)
            print(len(data))
            socket.send(data)
            cam.releaseFrame(frame)
            count += 1

