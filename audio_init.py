import pyaudio
import socket
import select
import wave


class set_audio:
    def __init__(self, audio, savepath):
        self.audio = audio

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 4096
        self.wf = wave.open(savepath, 'wb')
        self.wf.setnchannels(self.CHANNELS)
        self.wf.setsampwidth(audio.get_sample_size(self.FORMAT))
        self.wf.setframerate(self.RATE)

        self.running = True

    def stop(self):
        self.running = False

    def server(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 标明IPV4以及采用协议
        self.read_list = [serversocket]
        serversocket.bind(('127.0.0.1', 4444))
        serversocket.listen(5)
        # Start recording
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True,
                                 frames_per_buffer=self.CHUNK, stream_callback=self.callback)

        print("recording...")

        try:
            while self.running:
                readable, _, errored = select.select(self.read_list, [], [])
                for s in readable:
                    if s is serversocket:
                        clientsocket, address = serversocket.accept()
                        self.read_list.append(clientsocket)
                        print(f"Connection from {address}")
                    else:
                        try:
                            data = s.recv(1024)
                            if not data:
                                print(f"Connection closed by {s.getpeername()}")
                                self.read_list.remove(s)
                                s.close()
                        except ConnectionResetError:
                            print(f"Connection reset by peer {s.getpeername()}")
                            self.read_list.remove(s)
                            s.close()
        except KeyboardInterrupt:
            pass

        print('finished recording')
        serversocket.close()
        # Stop recording, close stream
        stream.stop_stream()
        stream.close()
        self.audio.terminate()

    def callback(self, in_data, frame_count, time_info, status):
        for s in self.read_list[1:]:
            try:
                s.send(in_data)
            except BrokenPipeError:
                print(f"Broken pipe with {s.getpeername()}")
                self.read_list.remove(s)
                s.close()
        return in_data, pyaudio.paContinue

    def client(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 4444))
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, output=True,
                                 frames_per_buffer=self.CHUNK)
        print("Connected to server, starting playback...")

        try:
            while self.running:
                data = s.recv(self.CHUNK)
                if not data:
                    break
                stream.write(data)
                self.wf.writeframes(data)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Exception: {e}")

        print('Shutting down')
        s.close()
        stream.close()
        self.audio.terminate()

