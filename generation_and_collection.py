import numpy as np
import nidaqmx
import threading
import time
import matplotlib.pyplot as plt

######################################################################

def generate_sine_wave(frequency, amplitude, duration, sampling_rate):
    t = np.linspace(0, duration, int(duration * sampling_rate), endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    return signal

def collect_data_from_ni_card(task_name, channels, duration, sampling_rate, data_ready_event, collected_data):
    with nidaqmx.Task(task_name) as task:
        for channel in channels:
            task.ai_channels.add_ai_voltage_chan(channel, terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
        
        task.timing.cfg_samp_clk_timing(sampling_rate, samps_per_chan=int(duration * sampling_rate))

        data = task.read(number_of_samples_per_channel=int(duration * sampling_rate))
        collected_data.extend(data)
        data_ready_event.set()

def send_signal_to_ni_card(task_name, frequency, amplitude, duration, sampling_rate, data_ready_event):
    signal = generate_sine_wave(frequency, amplitude, duration, sampling_rate)

    with nidaqmx.Task(task_name) as task:
        task.ao_channels.add_ao_voltage_chan('Dev2/ao1', min_val=-10.0, max_val=10.0)
        task.timing.cfg_samp_clk_timing(sampling_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

        task.write(signal, auto_start=False)

        data_ready_event.clear()
        task.start()

        # Wait for the specified duration to collect data
        time.sleep(duration)
        task.stop()

        # Signal that data collection is complete
        data_ready_event.set()
        
######################################################################

if __name__ == "__main__":
    task_name_generate = "sine_wave_task"
    task_name_collect = "data_acquisition_task"
    channels = ["Dev2/ai3", "Dev2/ai2"]  # Replace with the appropriate AI channel on your NI card
    frequency = 46550  # Frequency of the sine wave (in Hz)
    amplitude = 1.5   # Amplitude of the sine wave (in volts)
    duration = 50.05    # Duration of the signal (in seconds)
    sampling_rate_collection = 700000  # Sampling rate (samples per second)
    sampling_rate_generate = 2000000  # Sampling rate (samples per second)

    data_ready_event = threading.Event()
    collected_data = []

    # Create two separate threads for generating the sine wave and collecting data
    collect_thread = threading.Thread(target=collect_data_from_ni_card, args=(task_name_collect, channels, duration, sampling_rate_collection, data_ready_event, collected_data))
    generate_thread = threading.Thread(target=send_signal_to_ni_card, args=(task_name_generate, frequency, amplitude, duration, sampling_rate_generate, data_ready_event))
    

    # Start the threads
    generate_thread.start()
    collect_thread.start()

    # Wait for both threads to finish
    generate_thread.join()
    collect_thread.join()

    # Plot the collected data
    num_samples_per_channel = int(duration * sampling_rate_collection)
    t = np.linspace(0, duration, num_samples_per_channel, endpoint=False)
    
    for i, channel_data in enumerate(np.array(collected_data).reshape(-1, num_samples_per_channel)):
        plt.plot(t, channel_data, label=f"Channel {i}")
    
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title('Collected Data from NI Card')
    plt.legend()
    plt.show()