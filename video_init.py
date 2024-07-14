import datetime
import socket
import sys
import threading
import numpy as np
import cv2
import time


class set_video:
    def __init__(self, cap, savepath):
        self.cap = cap

        # 创建视频文件
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.file = cv2.VideoWriter(savepath, fourcc, 30, (640, 480))

        self.server_ip = '127.0.0.1'
        self.server_port = 6666
        self.client_ip = '127.0.0.1'
        self.client_port = 6666

        self.running = True

    def stop(self):
        self.running = False  # 设置标志变量为False来停止连接
        print("connection stop")

    def server(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 标明IPV4以及采用协议
            s.bind((self.server_ip, self.server_port))  # 绑定端口以及ip地址
            s.listen(15)  # 监听
        except:
            sys.exit(1)
        print('Waiting connection...')
        while self.running:
            conn, addr = s.accept()  # 接收描述字和指针
            t = threading.Thread(target=self.deal_data, args=(conn, addr))  # 创建线程增加图片传输速率
            t.start()  # 开始线程

    # 加密图像数据
    def deal_data(self, conn, addr):
        print('Accept new connection from {0}'.format(addr))
        while self.running:
            ret, frame = self.cap.read()  # 读取视频帧
            # 加水印
            font = cv2.FONT_HERSHEY_SIMPLEX
            datet = str(datetime.datetime.now())
            text1 = 'eejhx'
            frame = cv2.putText(frame, datet, (10, 100), font, 1,(0, 255, 255), 2, cv2.LINE_AA)
            frame_watermark = cv2.putText(frame, text1, (10, 150), font, 0.9,(255, 0, 0), 2, cv2.LINE_AA)
            # enimage=encode(frame)#加密加过水印后的图像
            # 进行传输编码
            img = cv2.imencode('.jpg', frame_watermark)[1]
            data_encode = np.array(img)
            str_encode = data_encode.tobytes()
            try:
                conn.send(str_encode)  # 发送图片的encode码
            except:
                print('wait')
            time.sleep(0.02)
        conn.close()

    # 视频客户端设置
    def client(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.client_ip, self.client_port))  # 连接服务端
        except socket.error as msg:
            print(msg)
            sys.exit(1)
        print('this is Client')
        while self.running:
            try:
                receive_encode = s.recv(307200)  # 接收的字节数 最大值 2147483647 （31位的二进制）
                nparr_decode = np.fromstring(receive_encode, np.uint8)
                img_decode = cv2.imdecode(nparr_decode, cv2.IMREAD_COLOR)  # 图片解码
                self.file.write(img_decode)  # 写入视频帧
                cv2.imshow("jie mi", img_decode)

                # 当按下键盘esc时，退出录制
                if cv2.waitKey(1) == 27:
                    self.stop()
            except Exception as e:
                print(e)
