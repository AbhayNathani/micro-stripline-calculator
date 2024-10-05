import streamlit as st
import math

# Add custom CSS to reduce margin or padding
st.markdown(
    """
    <style>
    .main > div {
        padding-top: 1rem; /* Adjust padding at the top */
        max-width: 900px;  /* Set to your desired width */
        margin: auto;  /* Center the content */
    }

    </style>
    """, unsafe_allow_html=True
)

# Add a title at the top of the app
st.title("Abhi's Lab: Microstrip Line Calculator")

# Layout: Create two columns
col1, col2 = st.columns(2)

# Inputs in the first column
with col1:
    TARGET_IMPEDANCE = st.number_input("Target Impedance Z0 (Ω)", value=50.0, step=1.0)
    SUBSTRATE_HEIGHT = st.number_input("Substrate Height h (mm)", value=1.6, step=0.1)
    INITIAL_STEP_FRACTION = st.number_input("Initial Step Fraction", value=0.5, step=0.05)
    TOLERANCE = st.number_input("Tolerance (Ω)", value=0.01)

# Inputs in the second column
with col2:
    DIELECTRIC_CONSTANT = st.number_input("Dielectric Constant Er", value=4.4, step=0.1)
    ELECTRICAL_LENGTH = st.number_input("Electrical Length (degrees)", value=45.0, step=5.0)
    FREQUENCY = st.number_input("Frequency (GHz)", value=2.0) * 1e9  # Convert GHz to Hz

# Constants
SPEED_OF_LIGHT = 299792458  # Speed of light in m/s (constant)


# Hammerstad's effective dielectric constant calculation (with correction term for w/h <= 1)
def calc_effective_dielectric_constant(er, h, w):
    if w / h > 1:
        return (er + 1) / 2 + ((er - 1) / 2) * (1 / math.sqrt(1 + 12 * (h / w)))
    else:
        return (er + 1) / 2 + ((er - 1) / 2) * ( (1 / math.sqrt(1 + 12 * (h / w)) ) + 0.04 * (1 - w / h) ** 2)


# Hammerstad's characteristic impedance calculation for wide and narrow cases
def calc_characteristic_impedance(er_eff, h, w):
    if w / h <= 1:  # Narrow strip case
        return (60 / math.sqrt(er_eff)) * math.log(8 * h / w + w / (4 * h))
    else:  # Wide strip case
        return (120 * math.pi) / (math.sqrt(er_eff) * (w / h + 1.393 + 0.667 * math.log(w / h + 1.444)))


# Iterative approach with step size as a fraction of width
def find_microstrip_width(target_impedance, er, h, initial_width=0.1, step_fraction=0.05, tolerance=0.01):
    width = initial_width

    while True:
        # Calculate effective dielectric constant and impedance
        er_eff = calc_effective_dielectric_constant(er, h, width)
        z0 = calc_characteristic_impedance(er_eff, h, width)

        # Check if we're close enough to the target impedance
        if abs(z0 - target_impedance) < tolerance:
            return width, er_eff,z0,(abs(z0-target_impedance)*100)/target_impedance

        # Adjust the step size dynamically as a fraction of the current width
        step_size = step_fraction * width

        # Adjust width based on whether the impedance is too high or too low
        if z0 > target_impedance:
            width += step_size  # Increase width if impedance is too high
        else:
            width -= step_size  # Decrease width if impedance is too low

        # Ensure the width never becomes negative
        if width < 0.00001:
            st.write(f"NEGATIVE or Very LOW PROBLEM! Width: {width}")
            return width, er_eff


# Function to calculate physical length from electrical length
def calculate_physical_length(electrical_length, frequency, er_eff):
    # Calculate effective wavelength
    lambda_eff = SPEED_OF_LIGHT / (frequency * math.sqrt(er_eff))
    # Calculate physical length
    physical_length = lambda_eff * (electrical_length / 360)  # in meters
    return physical_length


# Main Calculation Logic - Perform calculations dynamically
width, er_eff,z0,error_percentage = find_microstrip_width(TARGET_IMPEDANCE, DIELECTRIC_CONSTANT, SUBSTRATE_HEIGHT,
                                      step_fraction=INITIAL_STEP_FRACTION, tolerance=TOLERANCE)
physical_length = calculate_physical_length(ELECTRICAL_LENGTH, FREQUENCY, er_eff)

# Display results using markdown
st.markdown(f"### Line Width $$(w)$$: `{width} mm`")
st.markdown(f"### Physical Length $$(l)$$: `{physical_length * 1000} mm`")  # Convert from meters to mm
st.markdown("### Effective Dielectric Constant $$(\epsilon_{eff})$$: " +  f"`{er_eff}`")
st.write(f"Found Solution for Z0 ={z0:.2f} Ω which is {(100-error_percentage):.3f}% accurate.")

st.header("Microstrip Line Layout and Calculations")

# Display an image for the microstrip layout
st.image("microstrip_layout.png", caption="Microstrip Line Layout.", use_column_width=True)

st.markdown(
    "The image above shows the basic layout of a microstrip line, including the width of the strip (w), the height of the substrate (h), and the ground plane.")

# Display equations and explanations
st.subheader("Equations Used")
st.markdown(
    """
    ### Hammerstad's Effective Dielectric Constant
    The effective dielectric constant ( $$ \epsilon_{eff} $$) is given by:

    $$
    \epsilon_{eff} =
    \\begin{cases}
    \\frac{\\epsilon_r + 1}{2} + \\frac{\\epsilon_r - 1}{2} \\cdot \\left( \\frac{1}{\\sqrt{1 + 12 \\cdot \\frac{h}{w}}} + 0.04 \\cdot \\left(1 - \\frac{w}{h}\\right)^2\\right) & \\text{if } \\frac{w}{h} \\leq 1 \\\\
    \\frac{\\epsilon_r + 1}{2} + \\frac{\\epsilon_r - 1}{2} \\cdot \\left( \\frac{1}{\\sqrt{1 + 12 \\cdot \\frac{h}{w}}} \\right) & \\text{if } \\frac{w}{h} > 1 \\\\
    \\end{cases}
    $$
    """
)

st.markdown(
    """
    ### Characteristic Impedance Calculation
    The characteristic impedance $$ Z_0 $$ is calculated using:

    $$
    Z_0 =
    \\begin{cases}
    \\frac{60}{\\sqrt{\\epsilon_{eff}}} \\cdot \\ln\\left(\\frac{8h}{w} + \\frac{w}{4h}\\right) & \\text{if } \\frac{w}{h} \\leq 1 \\\\
    \\frac{120\\pi}{\\sqrt{\\epsilon_{eff}} \\cdot \\left(\\frac{w}{h} + 1.393 + 0.667 \\ln\\left(\\frac{w}{h} + 1.444\\right)\\right)} & \\text{if } \\frac{w}{h} \\geq 1 \\\\
    \\end{cases}
    $$
    """
)

st.subheader("Explanation of Iterative Approach")
st.markdown(
    """
    The iterative approach is designed to adjust the width of the microstrip line to achieve the desired target impedance. It dynamically modifies the width based on the difference between the calculated impedance and the target impedance. The key parameters used in this approach are:

    - **Step Fraction**: Determines how much the width is adjusted during each iteration. A smaller fraction allows for finer adjustments, which is beneficial for achieving higher impedances and narrower widths.
    - **Tolerance**: Defines the acceptable range for the impedance calculation. A smaller tolerance can lead to more precise results but may require more iterations.

    This method effectively solves for higher impedances and lower widths without error, unlike many online calculators that may not account for the complex behavior of microstrip lines.
    """
)
