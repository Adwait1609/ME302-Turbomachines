import pandas as pd
import matplotlib.pyplot as plt

# ================
# Constants
# ================
gamma = 1.4                # Specific heat ratio
R = 287.0                  # Gas constant [J/kg·K]
mu = 1.83e-5               # Dynamic viscosity [Pa·s]
L_prototype = 0.2          # Prototype length [m]
M_target = 0.55            # Design Mach number
Re_target = 3.0e6          # Design Reynolds number
p_max = 250e3              # Max pressure [Pa]
T01 = 293.0                # Inlet stagnation temp [K]

# ================
# Core Calculation
# ================
def calculate_scale(row):
    """Calculate scale for a compressor operating point"""
    P0_ratio = row['P0_ratio']
    T0_ratio = row['T0_ratio']
    
    # Pressure calculations
    p01 = p_max / P0_ratio            # Inlet pressure
    p02 = p_max                       # Always 250 kPa (from p01 * P0_ratio)
    p04 = p02 * 0.985                 # After 1.5% loss
    T04 = T01 * T0_ratio              # Stagnation temperature at station 4
    
    # Static properties at station 4
    T4 = T04 / (1 + (gamma-1)/2 * M_target**2)
    p4 = p04 / ((1 + (gamma-1)/2 * M_target**2)**(gamma/(gamma-1)))
    rho4 = p4 / (R * T4)
    C4 = M_target * (gamma * R * T4)**0.5
    
    # Scale calculation
    L_model = (Re_target * mu) / (rho4 * C4)
    scale = L_model / L_prototype
    
    return scale if 0 <= scale <= 1 else None

# ================
# Main Execution
# ================
# Load and filter compressor map
df = pd.read_csv('Compressor_operation_map.txt', sep='\t', comment='#',
                 names=['mdot_ref', 'T0_ratio', 'P0_ratio'])
valid_df = df[df['P0_ratio'] >= 1.0686].copy()

# Calculate scales
valid_df['scale'] = valid_df.apply(calculate_scale, axis=1)
result_df = valid_df.dropna()

if not result_df.empty:
    # Find optimal point
    optimal = result_df.loc[result_df['scale'].idxmax()]
    
    # Generate plot
    plt.figure(figsize=(10, 6))
    
    # Plot all compressor points
    plt.plot(df['mdot_ref'], df['P0_ratio'], 'o', 
             markersize=5, alpha=0.5, label='All Points')
    
    # Plot valid points
    plt.plot(result_df['mdot_ref'], result_df['P0_ratio'], 's', 
             markersize=6, label='Valid Points')
    
    # Highlight optimal point
    plt.plot(optimal['mdot_ref'], optimal['P0_ratio'], '*', 
             markersize=12, label=f'Optimal Point\nScale = {optimal["scale"]:.3f}')
    
    plt.title('Compressor Operating Map')
    plt.xlabel('Reference Mass Flow Rate (kg/s)')
    plt.ylabel('Stagnation Pressure Ratio (P02/P01)')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Print results
    print(f"Maximum Scale: {optimal['scale']:.3f}")
    print(f"Operating Point:")
    print(f"• mdot_ref = {optimal['mdot_ref']:.3f} kg/s")
    print(f"• P0_ratio = {optimal['P0_ratio']:.4f}")
else:
    print("No valid solutions found!")