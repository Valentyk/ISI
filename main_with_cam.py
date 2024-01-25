import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import threading
import time

######################################################################

from generation_and_collection import send_signal_to_ni_card
from generation_and_collection import collect_data_from_ni_card
from cam import camera_capture
from cam import video_from_images

######################################################################

task_name_generate = "sine_wave_task"  
task_name_collect = "data_acquisition_task"
channels = ["Dev2/ai3", "Dev2/ai2"]  # Replace with the appropriate AI channel on your NI card
amplitude = 1.5   # Amplitude of the sine wave (in volts)
duration = 0.05    # Duration of the signal (in seconds)
sampling_rate_collection = 700000  # Sampling rate (samples per second)
sampling_rate_generate = 2000000  # Sampling rate (samples per second)

sampling_rate_frequency = 1/50 # Sampling rate of the frequencies
start_frequency = 42000 # Starting frequency of the sine pulses
end_frequency = 52000 # Final frequency of the sine pulses
frequency = np.linspace(start_frequency, end_frequency, int(sampling_rate_frequency*(end_frequency-start_frequency)+1)) # Frequency of the sine wave (in Hz)

fps = 200   #fps of the camera (currently fixed on 200 fps)
video_duration = (duration+0.05)*len(frequency)+3 #Duration of video is 1 sec longer than duration of the signal
total_frames = fps*video_duration   #How many frames should the camera take
video_rate = 60/200  #Speed of the recorded video (lowest value for 30 fps video output is 30/200)

courrent_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
file_name = f"C:/Users/User/Desktop/Piezo_Valentík/2023/Piezo_particles/2023/data/pure_data/video_{courrent_datetime}.mp4" #path of the saved file

print(frequency, len(frequency))

######################################################################
img = []

data_ready_event = threading.Event()

capture_thread = threading.Thread(target=camera_capture, args=(img, total_frames))

capture_thread.start()
time.sleep(0.75)

for i in range(len(frequency)):
    generate_thread = threading.Thread(target=send_signal_to_ni_card, args=(task_name_generate, frequency[i], amplitude, duration, sampling_rate_generate, data_ready_event))
    generate_thread.start()
    generate_thread.join()
print("generate done")

capture_thread.join()

video_from_images(img, file_name, fps*video_rate)

print("Done")