import tkinter as tk
from hackrf import HackRF

def set_frequency(value):
    hackrf_device.set_freq(int(value))

hackrf_device = HackRF()
hackrf_device.setup()
hackrf_device.start_rx_mode(None) # Add your RX callback here

root = tk.Tk()
root.title('Frequency Tuner')

slider = tk.Scale(root, from_=2400, to=2485, orient=tk.HORIZONTAL, command=set_frequency)
slider.pack()

root.mainloop()

hackrf_device.stop_rx()
hackrf_device.close()
