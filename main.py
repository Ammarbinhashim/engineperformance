import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt


# Function to calculate engine parameters
def calculate_performance():
    # Fetch input values
    bore = float(entry_bore.get())
    stroke = float(entry_stroke.get())
    num_cylinders = int(entry_cylinders.get())
    rated_bp = float(entry_bp.get())
    rated_rpm = float(entry_rpm.get())
    fuel_density = float(entry_density.get())
    calorific_value = float(entry_calorific.get())
    
    # Convert units if necessary
    if bore_units.get() == "inches":
        bore *= 0.0254
    if stroke_units.get() == "inches":
        stroke *= 0.0254
    if bp_units.get() == "HP":
        rated_bp *= 0.7457

    # Get load test type
    load_test_type = load_system.get()
    if load_test_type == "Rope Brake Dynamometer":
        R = float(entry_brake_radius.get())
        w_max = (4500 * rated_bp) / (2 * math.pi * rated_rpm * R)
    else:
        # Placeholder for Electric Generator calculations if needed
        w_max = 0

    # Calculate performance parameters
    area_of_cylinder = math.pi * (bore / 2) ** 2
    num_working_strokes_per_minute = rated_rpm / 2

    # Display maximum load
    lbl_max_load.config(text=f"Max Load (kg): {w_max:.2f}")

    # Simulated data for observation table
    observation_data = []
    step_load = w_max / 5
    bp_list = []
    sfc_list = []
    tfc_list = []
    bmep_list = []
    imep_list = []
    
    for i in range(6):
        load_kg = i * step_load
        load_lbs = load_kg * 2.20462
        time_10cc = 100 - (i * 10)  # Sample decreasing values for time
        tfc = (10 * fuel_density * 3600) / (time_10cc * 1000)
        bp = rated_bp * (i / 5)
        sfc = tfc / bp if bp != 0 else 0
        bmep = (bp * 60) / (stroke * area_of_cylinder * num_working_strokes_per_minute * num_cylinders)
        ip = bp + 1  # Simplified, replace with friction power logic
        imep = (ip * 60) / (stroke * area_of_cylinder * num_working_strokes_per_minute * num_cylinders)
        bte = (bp * 3600) / (tfc * calorific_value) * 100
        ite = (ip * 3600) / (tfc * calorific_value) * 100
        me = (bp / ip) * 100
        
        # Collect data for graphs
        bp_list.append(bp)
        sfc_list.append(sfc)
        tfc_list.append(tfc)
        bmep_list.append(bmep)
        imep_list.append(imep)
        
        # Append to observation data
        observation_data.append([i + 1, load_lbs, load_kg, time_10cc, tfc, sfc, bmep, ip, imep, bte, ite, imep])

    # Update observation table
    for row in table.get_children():
        table.delete(row)
    for data in observation_data:
        table.insert("", "end", values=data)

    # Plot graphs
    plot_graphs(bp_list, sfc_list, tfc_list, bmep_list, imep_list)


# Function to plot graphs
def plot_graphs(bp_list, sfc_list, tfc_list, bmep_list, imep_list):
    plt.figure(figsize=(10, 5))
    
    # Graph 1: BP vs SFC, TFC, BMEP, IMEP
    plt.subplot(1, 2, 1)
    plt.plot(bp_list, sfc_list, label="SFC", marker='o')
    plt.plot(bp_list, tfc_list, label="TFC", marker='o')
    plt.plot(bp_list, bmep_list, label="BMEP", marker='o')
    plt.plot(bp_list, imep_list, label="IMEP", marker='o')
    plt.xlabel("BP (kW)")
    plt.ylabel("Parameters")
    plt.title("BP vs SFC, TFC, BMEP, IMEP")
    plt.legend()
    
    # Graph 2: BP vs ME, ITE, BTE
    plt.subplot(1, 2, 2)
    plt.plot(bp_list, [me for me in sfc_list], label="ME", marker='o')
    plt.plot(bp_list, [ite for ite in tfc_list], label="ITE", marker='o')
    plt.plot(bp_list, [bte for bte in bmep_list], label="BTE", marker='o')
    plt.xlabel("BP (kW)")
    plt.ylabel("Efficiency")
    plt.title("BP vs ME, ITE, BTE")
    plt.legend()
    
    plt.tight_layout()
    plt.show()


# Create main window
root = tk.Tk()
root.title("4-Stroke Engine Performance")

# Input fields
tk.Label(root, text="Bore:").grid(row=0, column=0, sticky="e")
entry_bore = tk.Entry(root)
entry_bore.grid(row=0, column=1)
bore_units = ttk.Combobox(root, values=["inches", "meters"])
bore_units.grid(row=0, column=2)
bore_units.set("meters")

tk.Label(root, text="Stroke:").grid(row=1, column=0, sticky="e")
entry_stroke = tk.Entry(root)
entry_stroke.grid(row=1, column=1)
stroke_units = ttk.Combobox(root, values=["inches", "meters"])
stroke_units.grid(row=1, column=2)
stroke_units.set("meters")

tk.Label(root, text="Number of Cylinders:").grid(row=2, column=0, sticky="e")
entry_cylinders = tk.Entry(root)
entry_cylinders.grid(row=2, column=1)

tk.Label(root, text="Rated Brake Power:").grid(row=3, column=0, sticky="e")
entry_bp = tk.Entry(root)
entry_bp.grid(row=3, column=1)
bp_units = ttk.Combobox(root, values=["HP", "kW"])
bp_units.grid(row=3, column=2)
bp_units.set("kW")

tk.Label(root, text="Rated RPM:").grid(row=4, column=0, sticky="e")
entry_rpm = tk.Entry(root)
entry_rpm.grid(row=4, column=1)

tk.Label(root, text="Fuel Density (g/cc):").grid(row=5, column=0, sticky="e")
entry_density = tk.Entry(root)
entry_density.grid(row=5, column=1)

tk.Label(root, text="Calorific Value (kJ/kg):").grid(row=6, column=0, sticky="e")
entry_calorific = tk.Entry(root)
entry_calorific.grid(row=6, column=1)

# Load test selection
tk.Label(root, text="Load Test System:").grid(row=7, column=0, sticky="e")
load_system = ttk.Combobox(root, values=["Rope Brake Dynamometer", "Electric Generator"])
load_system.grid(row=7, column=1)
load_system.set("Rope Brake Dynamometer")

tk.Label(root, text="Mean Radius of Brake Drum (m):").grid(row=8, column=0, sticky="e")
entry_brake_radius = tk.Entry(root)
entry_brake_radius.grid(row=8, column=1)

# Calculate button
btn_calculate = tk.Button(root, text="Calculate", command=calculate_performance)
btn_calculate.grid(row=9, column=0, columnspan=3)

# Max load label
lbl_max_load = tk.Label(root, text="Max Load (kg): ")
lbl_max_load.grid(row=10, column=0, columnspan=3)

# Observation table
columns = ("SL No", "Load (lbs)", "Load (kg)", "Time for 10cc", "TFC", "SFC", "BMEP", "IP", "IMEP", "BTE", "ITE", "IMEP")
table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
table.grid(row=11, column=0, columnspan=3)

# Run the GUI
root.mainloop()
