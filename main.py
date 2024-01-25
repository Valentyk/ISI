import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import threading
import os

######################################################################

from generation_and_collection import send_signal_to_ni_card
from generation_and_collection import collect_data_from_ni_card

######################################################################

task_name_generate = "sine_wave_task"  
task_name_collect = "data_acquisition_task"
channels = ["Dev2/ai3", "Dev2/ai2"]  # Replace with the appropriate AI channel on your NI card
amplitude = 5.5   # Amplitude of the sine wave (in volts)
duration = 0.05    # Duration of the signal (in seconds)
sampling_rate_collection = 700000  # Sampling rate (samples per second)
sampling_rate_generate = 2000000  # Sampling rate (samples per second)

sampling_rate_frequency = 1/50 # Sampling rate of the frequencies
start_frequency = 40000 # Starting frequency of the sine pulses
end_frequency = 60000 # Final frequency of the sine pulses
frequency = np.linspace(start_frequency, end_frequency, int(sampling_rate_frequency*(end_frequency-start_frequency)+1)) # Frequency of the sine wave (in Hz)

print(frequency, len(frequency))

data = pd.DataFrame({
    "Frequency [Hz]": [],
    "Amplitude [V]": [],
    "STD x": [],
    "STD y": []
})

data_all = pd.DataFrame({
    "frequency [Hz]": [],
    "Amplitude [V]": [],
    "time [s]": [],
    "deviation x": [],
    "deviation y": []
})

######################################################################
for i in range(len(frequency)):
    data_ready_event = threading.Event()
    collected_data = []

    # Create two separate threads for generating the sine wave and collecting data
    generate_thread = threading.Thread(target=send_signal_to_ni_card, args=(task_name_generate, frequency[i], amplitude, duration, sampling_rate_generate, data_ready_event))
    collect_thread = threading.Thread(target=collect_data_from_ni_card, args=(task_name_collect, channels, duration, sampling_rate_collection, data_ready_event, collected_data))

    # Start the threads
    generate_thread.start()
    collect_thread.start()

    # Wait for both threads to finish
    generate_thread.join()
    collect_thread.join()

    # Plot the collected data
    num_samples_per_channel = int(duration * sampling_rate_collection)
    t = np.linspace(0, duration, num_samples_per_channel, endpoint=False)
    
    #GPT way of plotting
    # for i, channel_data in enumerate(np.array(collected_data).reshape(-1, num_samples_per_channel)):
    #     plt.plot(t, channel_data, label=f"Channel {i}")
    
    # plt.xlabel('Time (s)')
    # plt.ylabel('Voltage (V)')
    # plt.title('Collected Data from NI Card')
    # plt.legend()
    # plt.show()
    
    #My way of plotting
    # for n in range(len(collected_data)):
    #     plt.plot(t, collected_data[n], label = f"Channel {n}")
        
    # plt.xlabel('Time (s)')
    # plt.ylabel('Voltage (V)')
    # plt.title('Collected Data from NI Card')
    # plt.legend()
    # plt.show()    
            
    #Save std deviation
    data_new_line = pd.DataFrame({
        "Frequency [Hz]": [frequency[i]],
        "Amplitude [V]": [amplitude],
        "STD x": [np.std(collected_data[0])],
        "STD y": [np.std(collected_data[1])]
    })
    data = pd.concat([data, data_new_line], ignore_index = True)
    
    #Save all data (messy formating, sorry)
    # data_all_new_line = pd.DataFrame({
    #     "Frequency [Hz]": [frequency[i]],
    #     "Amplitude [V]": [amplitude],
    #     "time [s]": [t],
    #     "deviation x": [collected_data[0]],
    #     "deviation y": [collected_data[1]]    
    # })    
    # data_all = pd.concat([data_all, data_all_new_line], ignore_index= True)

courrent_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

parent_directory = f"C:/Users/User/Desktop/Piezo_Valentík/2023/Piezo_particles/2023/data/pure_data"
directory_name = f"data_{courrent_datetime}"
file_name = f"{start_frequency}-{end_frequency}_Hz.csv"
file_name_all_data = "data_all.csv"
graph_name = f"{start_frequency}-{end_frequency}_Hz_plot.pdf"

path = os.path.join(parent_directory, directory_name)

os.mkdir(path)

data.to_csv(f"{path}/{file_name}")
#data_all.to_csv(f"{path}/{file_name_all_data}")

plt.style.use("ggplot")

plt.plot(data.iloc[:,0], data.iloc[:,2], label = "STD x", linewidth = 0.5, linestyle = ":")
plt.plot(data.iloc[:,0], data.iloc[:,3], label = "STD y", linewidth = 0.5, linestyle = ":")
plt.plot(data.iloc[:,0], (data.iloc[:,2]+data.iloc[:,3])/2, label = "Average value", linewidth = 0.75)

plt.xlabel("Frequency [Hz]")
plt.ylabel("STD")
plt.title(f"Napětí před zesílením $U = {amplitude}$V")

plt.legend()
plt.savefig(f"{path}/{graph_name}")
plt.show()