import tkinter as tk
from tkinter import ttk, messagebox
import math
import matplotlib.pyplot as plt

def enter_time_for_fuel_consumption(w_max, step_load):
    """
    Collect user input for time for 10cc fuel consumption at each load step.
    """
    def submit_times():
        try:
            # Collect time values from input fields
            time_values = {}
            for i, entry in enumerate(time_entries):
                time_values[i] = float(entry.get())
                if time_values[i] <= 0:
                    raise ValueError("Time must be positive.")
            time_input_window.destroy()
            calculate_performance(w_max, step_load, time_values)  # Pass time_values to calculate_performance
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    time_input_window = tk.Toplevel(root)
    time_input_window.title("Enter Time for 10cc Fuel Consumption")
    tk.Label(time_input_window, text="Enter time for each load step (seconds):").pack()
    time_entries = []
    for i in range(6):  # Assuming 6 steps (including no load)
        frame = tk.Frame(time_input_window)
        frame.pack()
        tk.Label(frame, text=f"Load Step {i + 1}:").pack(side=tk.LEFT)
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT)
        time_entries.append(entry)
    submit_button = tk.Button(time_input_window, text="Submit", command=submit_times)
    submit_button.pack()


def calculate_performance(w_max, step_load, time_values):
    try:
        # Fetch and validate input values
        bore = float(entry_bore.get())
        stroke = float(entry_stroke.get())
        num_cylinders = int(entry_cylinders.get())
        rated_bp = float(entry_bp.get())
        rated_rpm = float(entry_rpm.get())
        fuel_density = float(entry_density.get())
        calorific_value = float(entry_calorific.get())

        # Unit conversion - Get selected units for bore, stroke, and brake power
        bore_units_val = bore_units.get()  # Get the selected unit for bore
        stroke_units_val = stroke_units.get()  # Get the selected unit for stroke
        bp_units_val = bp_units.get()  # Get the selected unit for brake power

        if bore_units_val == "inches":
            bore *= 0.0254  # Convert inches to meters
        if stroke_units_val == "inches":
            stroke *= 0.0254  # Convert inches to meters
        if bp_units_val == "HP":
            rated_bp *= 0.7457  # Convert HP to kW

        # Load test type
        load_test_type = load_system.get()
        if load_test_type == "Rope Brake Dynamometer":
            try:
                R = float(entry_brake_radius.get())
                if R <= 0:
                    raise ValueError("Mean radius must be positive.")
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid mean radius for the brake drum.")
                return

            # Calculate maximum load (w_max in kg)
            w_max = (4500 * rated_bp) / (2 * math.pi * rated_rpm * R)
        else:
            # If using an electric generator, max load calculation might differ or be predefined
            w_max = 0  # Adjust this logic as needed

        # Ensure that inputs are positive and make sense
        if bore <= 0 or stroke <= 0 or num_cylinders <= 0 or rated_bp <= 0 or rated_rpm <= 0 or fuel_density <= 0 or calorific_value <= 0:
            raise ValueError("All input values must be positive.")

        step_load = w_max / 5  
        enter_time_for_fuel_consumption(w_max, step_load)  # Now passing w_max and step_load
        
        # Calculate cylinder area
        area_of_cylinder = math.pi * (bore / 2) ** 2
        num_working_strokes_per_minute = rated_rpm / 2

        # Display maximum load
        lbl_max_load.config(text=f"Max Load (kg): {w_max:.2f}")

        # Generate observation data
        observation_data = []
        bp_list = []
        sfc_list = []
        tfc_list = []
        bmep_list = []
        imep_list = []
        me_list = []
        bte_list = []
        ite_list = []

        for i in range(6):
            load_kg = i * step_load
            load_lbs = load_kg * 2.20462
            time_10cc = time_values[i]  # Using values from time_values
            tfc = (10 * fuel_density * 3600) / (time_10cc * 1000)  # TFC in kg/h
            bp = rated_bp * (i / 5)  # Linear scaling for example
            sfc = tfc / bp if bp != 0 else 0
            bmep = (bp * 60) / (stroke * area_of_cylinder * num_working_strokes_per_minute * num_cylinders)
            ip = bp + 1  # Simplified estimation of IP
            imep = (ip * 60) / (stroke * area_of_cylinder * num_working_strokes_per_minute * num_cylinders)
            bte = (bp * 3600) / (tfc * calorific_value) * 100 if tfc != 0 else 0
            ite = (ip * 3600) / (tfc * calorific_value) * 100 if tfc != 0 else 0
            me = (bp / ip) * 100 if ip != 0 else 0

            # Collect data for graphs
            bp_list.append(bp)
            sfc_list.append(sfc)
            tfc_list.append(tfc)
            bmep_list.append(bmep)
            imep_list.append(imep)
            me_list.append(me)
            bte_list.append(bte)
            ite_list.append(ite)

            # Append to observation data
            observation_data.append([i + 1, load_lbs, load_kg, time_10cc, tfc, sfc, bmep, ip, imep, bte, ite, imep])

        # Update observation table
        for row in table.get_children():
            table.delete(row)
        for data in observation_data:
            table.insert("", "end", values=data)

        # Plot graphs
        plot_graphs(bp_list, sfc_list, tfc_list, bmep_list, imep_list, me_list, bte_list, ite_list)

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))


def plot_graphs(bp_list, sfc_list, tfc_list, bmep_list, imep_list, me_list, bte_list, ite_list):
    plt.figure(figsize=(12, 6))

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
    plt.grid(True)

    # Graph 2: BP vs ME, ITE, BTE
    plt.subplot(1, 2, 2)
    plt.plot(bp_list, me_list, label="ME", marker='o')
    plt.plot(bp_list, ite_list, label="ITE", marker='o')
    plt.plot(bp_list, bte_list, label="BTE", marker='o')
    plt.xlabel("BP (kW)")
    plt.ylabel("Efficiency (%)")
    plt.title("BP vs ME, ITE, BTE")
    plt.legend()
    plt.grid(True)

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

tk.Label(root, text="Brake Power:").grid(row=3, column=0, sticky="e")
entry_bp = tk.Entry(root)
entry_bp.grid(row=3, column=1)
bp_units = ttk.Combobox(root, values=["kW", "HP"])
bp_units.grid(row=3, column=2)
bp_units.set("kW")

tk.Label(root, text="Rated RPM:").grid(row=4, column=0, sticky="e")
entry_rpm = tk.Entry(root)
entry_rpm.grid(row=4, column=1)

tk.Label(root, text="Fuel Density:").grid(row=5, column=0, sticky="e")
entry_density = tk.Entry(root)
entry_density.grid(row=5, column=1)

tk.Label(root, text="Calorific Value:").grid(row=6, column=0, sticky="e")
entry_calorific = tk.Entry(root)
entry_calorific.grid(row=6, column=1)

# Dynamometer option
tk.Label(root, text="Load Test Type:").grid(row=7, column=0, sticky="e")
load_system = ttk.Combobox(root, values=["Rope Brake Dynamometer", "Electric Generator"])
load_system.grid(row=7, column=1)
load_system.set("Rope Brake Dynamometer")

tk.Label(root, text="Brake Radius (m):").grid(row=8, column=0, sticky="e")
entry_brake_radius = tk.Entry(root)
entry_brake_radius.grid(row=8, column=1)

# Button to calculate performance
calculate_button = tk.Button(root, text="Calculate Performance", command=lambda: enter_time_for_fuel_consumption(0, 0))
calculate_button.grid(row=9, column=1)

# Observation Table
table_frame = tk.Frame(root)
table_frame.grid(row=10, column=0, columnspan=3)
table = ttk.Treeview(table_frame, columns=("Step", "Load (lbs)", "Load (kg)", "Time for 10cc (s)", "TFC (kg/h)", "SFC (g/kWh)", "BMEP (MPa)", "BP (kW)", "IMEP (MPa)", "BTE (%)", "ITE (%)", "IMEP"))
for col in table["columns"]:
    table.heading(col, text=col)
table.pack()

# Max load label
lbl_max_load = tk.Label(root, text="Max Load (kg): 0")
lbl_max_load.grid(row=9, column=0)

root.mainloop()
