import tkinter as tk
from tkinter import ttk, messagebox
import math
import matplotlib.pyplot as plt


def calculate_performance():
    try:
        # Fetch and validate input values
        bore = float(entry_bore.get())
        stroke = float(entry_stroke.get())
        num_cylinders = int(entry_cylinders.get())
        rated_bp = float(entry_bp.get())
        rated_rpm = float(entry_rpm.get())
        fuel_density = float(entry_density.get())
        calorific_value = float(entry_calorific.get())

        # Unit conversion
        if bore_units.get() == "inches":
            bore *= 0.0254  # Convert inches to meters
        if stroke_units.get() == "inches":
            stroke *= 0.0254  # Convert inches to meters
        if bp_units.get() == "HP":
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

        # Calculate cylinder area
        area_of_cylinder = math.pi * (bore / 2) ** 2
        num_working_strokes_per_minute = rated_rpm / 2

        # Display maximum load
        lbl_max_load.config(text=f"Max Load (kg): {w_max:.2f}")

        # Generate observation data
        step_load = w_max / 5
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
            time_10cc = 100 - (i * 10)  # Example values; replace with real observations
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
btn_calculate = tk.Button(root, text="Calculate Performance", command=calculate_performance)
btn_calculate.grid(row=9, column=0, columnspan=3)

# Maximum load display
lbl_max_load = tk.Label(root, text="Max Load (kg): -")
lbl_max_load.grid(row=10, column=0, columnspan=3)

# Observation table
columns = ("SL No", "Load (lbs)", "Load (kg)", "Time for 10cc", "TFC", "SFC", "BMEP", "IP", "IMEP", "BTE", "ITE", "IMEP")
table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
table.grid(row=11, column=0, columnspan=3)

# Run the main loop
root.mainloop()

    
