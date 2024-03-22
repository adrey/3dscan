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



client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # instantiate
client_socket.bind(("", 8099))  # connect to the server


def print_value(s):
    print('value: {}'.format(s))


cv2.namedWindow("preview", cv2.WINDOW_AUTOSIZE)

msg_size = 43200
msg = b'';
cur_frame = 0
buf = {}
# Process tasks forever
chunks = 5
while True:
    raw = client_socket.recvfrom(43202)
    sender = raw[1]
    print(raw[0][0])
    frame = raw[0][0]
    t = raw[0][1]
    raw = raw[0][2:]
    print(f"received {frame} {t} {len(raw)} {sender}")
    if frame != cur_frame:
      cur_frame = frame
      buf = {t: raw}
      continue
    else:
      buf[t] = raw
    if len(buf) != chunks:
      continue
   
    data = np.frombuffer(bytearray(buf[1]), dtype=np.uint8)
    data = np.reshape(data, newshape=(180, 240))
    depth_buf = np.frombuffer(bytearray(buf[2] + buf[3] + buf[4] + buf[5]), dtype=np.float32)
    depth_buf = np.reshape(depth_buf, newshape=(180, 240))
    amplitude_buf = data
    #amplitude_buf*=(255/1024)
    amplitude_buf = np.clip(amplitude_buf, 0, 255)

    cv2.imshow("preview_amplitude", amplitude_buf.astype(np.uint8))
    #print("select Rect distance:",np.mean(depth_buf[selectRect.start_y:selectRect.end_y,selectRect.start_x:selectRect.end_x]))

    result_image = process_frame(depth_buf,amplitude_buf)
    result_image = cv2.applyColorMap(result_image, cv2.COLORMAP_JET)
    #cv2.rectangle(result_image,(selectRect.start_x,selectRect.start_y),(selectRect.end_x,selectRect.end_y),(128,128,128), 1)

    cv2.imshow("preview",result_image)
    t2 = round(time.time() * 1000)
    #print(f"DIFF {t2 - t1}")
    key = cv2.waitKey(1)
    if key == ord("q"):
        exit_ = True
        sys.exit(0)

