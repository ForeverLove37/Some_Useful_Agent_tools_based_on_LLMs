# 002.py
# A test script for analyzing and visualizing product sales data.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Data Generation ---
# Create a sample dataset simulating sales for three products over a year.
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
data = {
    'Month': months,
    'Product_A_Sales': np.random.randint(100, 500, size=12),
    'Product_B_Sales': np.random.randint(150, 600, size=12),
    'Product_C_Sales': np.random.randint(80, 450, size=12)
}
sales_df = pd.DataFrame(data)

# Set Month as the index for easier plotting
sales_df.set_index('Month', inplace=True)

# --- Data Processing ---
# Calculate the total sales for each product for the entire year.
total_sales = sales_df.sum()
products = ['Product A', 'Product B', 'Product C']

# --- Visualization ---
# We will create two subplots to show different aspects of the data.
fig = plt.figure(figsize=(8, 10))
plt.style.use('seaborn-v0_8-whitegrid')

# Subplot 1: Bar chart for total sales comparison
# This chart compares the overall performance of the products.
ax1 = fig.add_subplot(2, 1, 1)
ax1.bar(products, total_sales, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
ax1.set_title('Total Annual Sales by Product')
ax1.set_ylabel('Total Sales (Units)')
ax1.set_xlabel('Product Name')

# Adding data labels on top of the bars
for i, val in enumerate(total_sales):
    ax1.text(i, val + 10, str(val), ha='center', va='bottom')

# Subplot 2: Line chart for monthly sales trends
# This chart shows the sales fluctuation over the year.
ax2 = fig.add_subplot(2, 1, 2)
sales_df.plot(ax=ax2, marker='o') # Plotting directly from pandas dataframe
ax2.set_title('Monthly Sales Trend')
ax2.set_ylabel('Monthly Sales (Units)')
ax2.set_xlabel('Month of the Year')
ax2.legend(['Sales of Product A', 'Sales of Product B', 'Sales of Product C'])
ax2.tick_params(axis='x', rotation=45)

# Ensure the layout is clean
plt.tight_layout()

# Finally, display the generated plots.
print("Plot generation complete. Displaying window...")
plt.show()

# End of the script.