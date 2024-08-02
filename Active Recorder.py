import os
import time
import threading
import tkinter as tk
import wave
import pyaudio
import speech_recognition as sr
import audioop

class activerecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Active Recorder")
        self.root.resizable(False, False)

        self.button = tk.Button(text="Start Recording", font=("Arial", 20, "bold"), command=self.changeRecording)
        self.button.pack(pady=20)

        self.label = tk.Label(text="00:00:00", font=("Arial",16))
        self.label.pack()

        self.statusLabel = tk.Label(text="Not Recording", font=("Arial", 12))
        self.statusLabel.pack(pady=10)

        self.recording = False
        self.frames = []
        self.startTime = 0

        self.root.mainloop()


    def changeRecording(self):
        if self.recording:
            self.recording = False
            self.button.config(text="Start recording", fg="black")
            self.saveRecording()
        else:
            self.recording = True
            self.button.config(text="Stop Recording", fg="red")
            self.frames = []
            self.startTime = time.time()
            threading.Thread(target=self.record).start()

    
    def updateTimer(self):
        if self.recording:
            elapsed = time.time() - self.startTime
            secs = elapsed % 60
            mins = elapsed // 60
            hours = mins // 60
            self.label.config(text=f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")
            self.root.after(1000,self.updateTimer)

    def record(self):
        chunk = 1024
        sampleFormat = pyaudio.paInt16
        channels = 1
        frameRate = 44100

        pyAudio = pyaudio.PyAudio()
        stream = pyAudio.open(format=sampleFormat, channels=channels, rate=frameRate, frames_per_buffer=chunk, input=True)

        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)

        self.updateTimer()

        silenceThreshold = 300
        silencetime = 1.0
        isSpeaking = False
        silenceChunks = 0
        chuncksPerSecond = int(frameRate / chunk)
        silentChunksThreshold = int(silencetime * chuncksPerSecond)

        while self.recording:
            data = stream.read(chunk)

            if isSpeaking:
                self.frames.append(data)

            energy = audioop.rms(data, 2)
            if energy > silenceThreshold:
                if not isSpeaking:
                    isSpeaking = True
                    self.root.after(0, lambda: self.statusLabel.config(text="Recording"))
                silenceChunks = 0
            else:
                silenceChunks += 1
                if silenceChunks > silentChunksThreshold and isSpeaking:
                    isSpeaking = False
                    self.root.after(0, lambda: self.statusLabel.config(text="Silence is Detected"))

        stream.stop_stream()
        stream.close()
        pyAudio.terminate()

    
    def saveRecording(self):
        if not self.frames:
            self.statusLabel.config("No audio recorded")
            return
        
        i = 1
        while os.path.exists(f"recording_{i}.wav"):
            i += 1

        filename = f"recording_{i}.wav"

        writingFrame = wave.open(filename, "wb")
        writingFrame.setnchannels(1)
        writingFrame.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        writingFrame.setframerate(44100)
        writingFrame.writeframes(b''.join(self.frames))
        writingFrame.close()

        self.statusLabel.config(text=f"Recording saved as {filename}")


if __name__ == "__main__":
    activerecorder()
