import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import threading
import time

######################################################################

from generation_and_collection import send_signal_to_ni_card
from cam import camera_capture
from cam import video_from_images

######################################################################

task_name_generate = "sine_wave_task"  
task_name_collect = "data_acquisition_task"
channels = ["Dev2/ai3", "Dev2/ai2"]  # Replace with the appropriate AI channel on your NI card
amplitude = 1.5   # Amplitude of the sine wave (in volts)
duration = 0.30    # Duration of the signal (in seconds) - 0.05s is enough for signal to reach maximal deviation. 
sampling_rate_generate = 2000000  # Sampling rate (samples per second)
frequency = 45500.0 # Frequency of the sine wave (in Hz)

fps = 200   #fps of the camera (this parameter must be modified in pylon viewer, then the fps value needs to be inserted here)
video_duration = duration + 3   #Duration of video is 3 sec longer than duration of the signal
total_frames = fps*video_duration   #How many frames should the camera take
video_rate = 60/200  #Speed of the recorded video (lowest value for 30 fps video output is 30/[current fps])

courrent_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
file_name = f"C:/Users/User/Desktop/Piezo_Valentík/2023/Piezo_particles/2023/data/pure_data/video_{courrent_datetime}.mp4" #path of the saved file
######################################################################
img = []

data_ready_event = threading.Event()

capture_thread = threading.Thread(target=camera_capture, args=(img, total_frames))
generate_thread = threading.Thread(target=send_signal_to_ni_card, args=(task_name_generate, frequency, amplitude, duration, sampling_rate_generate, data_ready_event))

capture_thread.start()
time.sleep(0.75)
generate_thread.start()

generate_thread.join()
capture_thread.join()

video_from_images(img, file_name, fps*video_rate)

print("Done")