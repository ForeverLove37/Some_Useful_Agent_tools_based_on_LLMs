import numpy as np
import matplotlib.pyplot as plt

# This script simulates and plots a noisy Gaussian signal.
# The core formula is the Gaussian function:
# f(x) = A * exp(-(x - mu)^2 / (2 * s^2))
# where A is amplitude, mu is the mean, and s is the standard deviation.

def generate_data(num_points):
    # Generate x values
    x = np.linspace(-10, 10, num_points)

    # Parameters for the Gaussian
    amplitude = 1.0 # The peak height
    mu = 0    # The center of the peak
    sigma = 2.0   # The width of the peak

    # Calculate the pure Gaussian signal
    y = amplitude * np.exp(-((x - mu)**2) / (2 * sigma**2))

    # Add some random noise
    noise = np.random.normal(0, 0.1, num_points)
    y_data = y + noise

    return x, y_data

# Number of data points
num_points = 500
x_data, y_data = generate_data(num_points)

# Plot the results
plt.figure(figsize=(8, 6))
plt.plot(x_data, y_data, label='Noisy Gaussian Signal')
plt.title('Simulation of a Gaussian Signal with Noise')
plt.xlabel('X-axis')
plt.ylabel('Signal Value')
plt.legend()
plt.grid(True)
plt.show()