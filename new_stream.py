import cv2
import os
import datetime
import pyaudio

from concurrent.futures import ThreadPoolExecutor
import video_init
import audio_init

if __name__ == "__main__":
    # 设置摄像头显示画面的大小
    cap = cv2.VideoCapture(0)  # 调  取内部摄像头
    # 调用windows内部声卡
    sound = pyaudio.PyAudio()


    # 设置日期
    now = str(datetime.datetime.now())[:19].replace(':', '_')
    dirName = now[:10]  # 目录名
    video_savepath = dirName + '//' + now + '.avi'  # 视频文件名
    audio_savepath = dirName + '//' + 'wav' + '//' + now + '.wav'
    # 创建wav目录
    wav_dir = os.path.join(dirName, 'wav')
    if not os.path.isdir(dirName):  # 创建目录
        os.mkdir(dirName)
    if not os.path.isdir(wav_dir):
        os.mkdir(wav_dir)

    video = video_init.set_video(cap, video_savepath)
    audio = audio_init.set_audio(sound, audio_savepath)

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(video.client)
        executor.submit(audio.client)
        executor.submit(video.server)
        executor.submit(audio.server)

