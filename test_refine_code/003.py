import numpy as np
import matplotlib.pyplot as plt

# This script simulates and plots a noisy Gaussian signal.
# The core formula is the Gaussian function:
# f(x) = A * exp(-(x - mu)^2 / (2 * s^2))
# where A is amplitude, mu is the mean, and s is the standard deviation.

def generate_data(points):
    # Generate x values
    temp_var = np.linspace(-10, 10, points)

    # Parameters for the Gaussian
    amplitude = 1.0 # The peak height
    mean_val = 0    # The center of the peak
    std_dev = 2.0   # The width of the peak

    # Calculate the pure Gaussian signal
    gauss_val = amplitude * np.exp(-((temp_var - mean_val)**2) / (2 * std_dev**2))

    # Add some random noise
    noise = np.random.normal(0, 0.1, points)
    final_signal = gauss_val + noise

    return temp_var, final_signal

# Number of data points
num_pts = 500
x_ax, y_ax = generate_data(num_pts)

# Plot the results
plt.figure(figsize=(8, 6))
plt.plot(x_ax, y_ax, label='Noisy Gaussian Signal')
plt.title('Simulation of a Gaussian Signal with Noise')
plt.xlabel('X-axis')
plt.ylabel('Signal Value')
plt.legend()
plt.grid(True)
plt.show()