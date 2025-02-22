!pip install scikit-learn pandas numpy matplotlib
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

def estimate_trigger_temperature(df, cell_type, trigger_mechanism):
    subset = df[
        (df['Cell-Description'] == cell_type) & 
        (df['Trigger-Mechanism'] == trigger_mechanism) &
        (df['Avg-Cell-Temp-At-Trigger-degC'].notna())
    ]
    
    if subset.empty:
        return None, None, "No data available for this cell type and trigger mechanism."
    
    temperatures = subset['Avg-Cell-Temp-At-Trigger-degC'].values
    
    n = len(temperatures)
    std_dev = np.std(temperatures)
    bandwidth = 1.06 * std_dev * (n ** (-1/5))
    
    kde = gaussian_kde(temperatures, bw_method=bandwidth / std_dev)  # Normalize bandwidth
    
    temp_range = np.linspace(min(temperatures) - 20, max(temperatures) + 20, 1000)
    kde_values = kde(temp_range)
    
    mode_idx = np.argmax(kde_values)
    mode_temp = temp_range[mode_idx]
    
    plt.figure(figsize=(10, 6))
    plt.plot(temp_range, kde_values, label='KDE Estimate')
    plt.axvline(mode_temp, color='red', linestyle='--', label=f'Mode: {mode_temp:.2f}°C')
    plt.scatter(temperatures, [0] * len(temperatures), color='blue', label='Data Points', zorder=5)
    plt.title(f'Temperature Distribution for {cell_type} ({trigger_mechanism})')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return mode_temp, temperatures, f"Estimated most likely temperature: {mode_temp:.2f}°C"

file_path = 'battery_data_failure.csv'  
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please check the file path.")
    exit()

cell_type = "KULR 18650-K330"
trigger_mechanism = "Heater (ISC)"

mode_temp, temps, message = estimate_trigger_temperature(df, cell_type, trigger_mechanism)
print(f"Cell Type: {cell_type}")
print(f"Trigger Mechanism: {trigger_mechanism}")
print(f"Data Points: {temps}")
print(message)
