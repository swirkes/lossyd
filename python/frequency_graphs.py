import matplotlib.pyplot as plt
import numpy as np

# Starting and ending frequencies
start_freq = 2476000000
end_freq = 2481000000

# Frequency step
freq_step = 454545.45

# Amplitude measurements at each frequency point
amplitudes = [-60.31, -61.39, -67.31, -75.24, -62.29, -57.43, -59.68, -63.6, -60.32, -64.99, -66.88]

# Correcting the graph to plot a single line with each frequency point corresponding to a specific amplitude

# Adjusting the frequency points to match the number of amplitude measurements
# Ensuring that the frequencies and amplitudes have the same length
freq_points = np.linspace(start_freq, end_freq, len(amplitudes))

# Mapping the original frequency values to a range between 20 and 20,000 Hz both linearly and logarithmically

# Function to map old range to new range linearly
def map_linear(old_value, old_min, old_max, new_min, new_max):
    return (((old_value - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min

# Function to map old range to new range logarithmically
def map_logarithmic(old_value, old_min, old_max, new_min, new_max):
    # Convert the old range into a logarithmic scale, then map it
    log_old_min = np.log10(old_min)
    log_old_max = np.log10(old_max)
    log_old_value = np.log10(old_value)
    return 10**(((log_old_value - log_old_min) * (np.log10(new_max) - np.log10(new_min))) / (log_old_max - log_old_min)) + new_min

# Applying the mapping to the frequency points
linear_mapped_freqs = [map_linear(freq, start_freq, end_freq, 20, 20000) for freq in freq_points]
log_mapped_freqs = [map_logarithmic(freq, start_freq, end_freq, 20, 20000) for freq in freq_points]


# Correcting the logarithmic mapping to ensure it ranges up to 20,000 Hz

# Revised function for logarithmic mapping
def map_logarithmic_corrected(old_value, old_min, old_max, new_min, new_max):
    # Normalizing the old value in the old range
    normalized_value = (np.log10(old_value) - np.log10(old_min)) / (np.log10(old_max) - np.log10(old_min))
    # Mapping the normalized value to the new logarithmic range
    return 10**(normalized_value * (np.log10(new_max) - np.log10(new_min)) + np.log10(new_min))

# Applying the corrected mapping to the frequency points
log_mapped_freqs_corrected = [map_logarithmic_corrected(freq, start_freq, end_freq, 20, 20000) for freq in freq_points]

# Plotting both mappings again
plt.figure(figsize=(12, 6))

# Linear mapping plot
plt.subplot(1, 2, 1)
plt.plot(linear_mapped_freqs, amplitudes, marker='o', linestyle='-', color='blue')
plt.title("Linearly Mapped Frequency vs Amplitude")
plt.xlabel("Frequency (20 to 20,000 Hz)")
plt.ylabel("Amplitude (dB)")
plt.grid(True)

# Corrected logarithmic mapping plot
plt.subplot(1, 2, 2)
plt.plot(log_mapped_freqs_corrected, amplitudes, marker='o', linestyle='-', color='green')
plt.title("Logarithmically Mapped Frequency vs Amplitude")
plt.xlabel("Frequency (20 to 20,000 Hz)")
plt.ylabel("Amplitude (dB)")
plt.grid(True)

plt.tight_layout()
plt.show()


# Plotting
plt.figure(figsize=(10, 6))
plt.plot(freq_points, amplitudes, marker='o', linestyle='-')

# Adjusting x-axis to show frequencies in GHz for readability
plt.xticks(ticks=freq_points, labels=[f"{freq/1e9:.3f}" for freq in freq_points])

plt.title("Frequency vs Amplitude")
plt.xlabel("Frequency (GHz)")
plt.ylabel("Amplitude (dB)")
plt.grid(True)
plt.show()

# Correcting the code to accurately display the GHz frequencies at the 2.4 GHz range 
# and the audible frequencies in the 20-20000 Hz range

# We use freq_points for the original GHz frequencies and linear_mapped_freqs for the audible frequencies.
# However, we must scale the audible frequencies down since they're too large compared to the GHz frequencies.
# To make them visible on the same plot, we'll scale them down by a factor of 1e9, just like the GHz frequencies.

# First, let's scale the audible frequencies to be in the range of the GHz frequencies for visual comparison
scaled_audible_freqs = [x / 1e9 for x in linear_mapped_freqs]

plt.figure(figsize=(10, 6))

# Plotting the original GHz frequencies with amplitudes
plt.plot(freq_points / 1e9, amplitudes, marker='o', linestyle='-', color='blue', label='Original GHz Frequencies')

# Plotting the scaled audible frequencies with amplitudes
plt.plot(scaled_audible_freqs, amplitudes, marker='x', linestyle='-', color='red', label='Mapped Audible Frequencies (scaled to GHz)')

plt.title("Comparison of Original GHz Frequencies and Scaled Audible Frequencies")
plt.xlabel("Frequency (GHz)")
plt.ylabel("Amplitude (dB)")
plt.legend()
plt.grid(True)
plt.show()
