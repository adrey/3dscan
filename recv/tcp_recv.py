import zmq
import pickle
import sys
import cv2
import time
import numpy as np
import ArducamDepthCamera as ac
import socket



MAX_DISTANCE = 4

def process_frame(depth_buf: np.ndarray, amplitude_buf: np.ndarray) -> np.ndarray:

    depth_buf = np.nan_to_num(depth_buf)

    amplitude_buf[amplitude_buf<=7] = 0
    amplitude_buf[amplitude_buf>7] = 255

    depth_buf = (1 - (depth_buf/MAX_DISTANCE)) * 255
    depth_buf = np.clip(depth_buf, 0, 255)
    result_frame = depth_buf.astype(np.uint8)  & amplitude_buf.astype(np.uint8)
    return result_frame

class UserRect():
    def __init__(self) -> None:
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

selectRect = UserRect()



client_socket = socket.socket()  # instantiate
client_socket.connect(("192.168.0.11", 8090))  # connect to the server


def print_value(s):
    print('value: {}'.format(s))


cv2.namedWindow("preview", cv2.WINDOW_AUTOSIZE)

msg_size = 172800
msg = b'';
# Process tasks forever
while True:
    raw = client_socket.recv(1350)
    if len(msg) + len(raw) > msg_size:
       diff = len(msg) + len(raw) - msg_size
       diff = len(raw) - diff
       cut = raw[:diff]
       msg = msg + cut
       print(len(msg))
       data = np.frombuffer(bytearray(msg), dtype=np.float32)
       msg = raw[diff:]
    else:
       msg = msg + raw
       continue
    data = np.reshape(data, newshape=(180, 240))
    print("received")
    amplitude_buf = data
    amplitude_buf.setflags(write=1)
    amplitude_buf*=(255/1024)
    amplitude_buf = np.clip(amplitude_buf, 0, 255)

    cv2.imshow("preview_amplitude", amplitude_buf.astype(np.uint8))
    #print("select Rect distance:",np.mean(depth_buf[selectRect.start_y:selectRect.end_y,selectRect.start_x:selectRect.end_x]))

    #result_image = process_frame(depth_buf,amplitude_buf)
    #result_image = cv2.applyColorMap(result_image, cv2.COLORMAP_JET)
    #cv2.rectangle(result_image,(selectRect.start_x,selectRect.start_y),(selectRect.end_x,selectRect.end_y),(128,128,128), 1)

    #cv2.imshow("preview",result_image)
    t2 = round(time.time() * 1000)
    #print(f"DIFF {t2 - t1}")
    key = cv2.waitKey(1)
    if key == ord("q"):
        exit_ = True
        sys.exit(0)

