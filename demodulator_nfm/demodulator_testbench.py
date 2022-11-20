
import numpy as np
import matplotlib.pyplot as plt
from demodulator_nfm import DemodulatorNFM

# =========== USER DEFINES =============
RECEIVER_SAMPLING_FREQUENCY = 100.0e3             # Hz - Frequency of local oscillator
# Ratio between sampling frequency and local oscillator frequency.
# It must be multiple of 4.
OVERSAMPLING_RATIO = 4 * 2
SAMPLING_FREQUENCY = OVERSAMPLING_RATIO * RECEIVER_SAMPLING_FREQUENCY  # Hz - ADC sampling frequency
# This parameter determines delay in polar discriminator
DISCRIMINATOR_DELAY_RATIO = 1

# Parameters of modulation signal:
FM1_CARRIER_FREQ = 106.7e3   # Hz - Carrier frequency of FM signal
FM1_AMPLITURE = 1            # units - Amplitude of carrier frequency in FM signal
FM1_FREQ_SENSITIVITY = 1000  #  - frequency sensitivity [ Hz/V ]
# List of frequency components in modulation signal
FM1_MOD_FREQ_LIST = [370, 962] # Hz
# List of amplitudes of frequency components in modulation signal
FM1_MOD_AMP_LIST =  [0.5,  0.5 ] # units - does not matter in the model (e.g. Volts or Amperes)

NUMBER_OF_SAMPLES = 8000     # Number of samples for simulation
CUT_SAMPLES_CNT = 150        # Number of samples at the beginning to skip transient process caused by IIR DF

# =========== USER DEFINES (end) =============

# Precalculations:

t_sampling = 1/SAMPLING_FREQUENCY
t_observation = t_sampling * (NUMBER_OF_SAMPLES)
print(f'Observation interval = {t_observation * 1e6} us')
print(f'Sampling period = {t_sampling * 1e6} us')

# This function to generate modulation signal used to modulate carrier frequency later
# Parameter modulation_freq_list is a list containing frequency components of modulation signal
# Parameter modulation_amp_list is a list containing amplitudes of frequency components of modulation signal
def generate_modulation_signal(time_vector, modulation_freq_list, modulation_amp_list):
    time_vect_len = len(time_vector)
    modulation_signal = np.zeros(time_vect_len)
    for freq, amplitude in zip(modulation_freq_list, modulation_amp_list):
        temp = amplitude * np.sin(time_vector * 2 * np.pi * freq)
        modulation_signal = modulation_signal + temp

    return modulation_signal

# Function to generate samples of FM signal using known modulation signal
def modulate_fm(time_vector, carrier_freq, carrier_amp, frequency_sensitivity, modulation_signal):
    sampling_period = 1 / carrier_freq
    samples_cnt = len(time_vector)
    phase_components =np.zeros(samples_cnt)
    # Calculate integral of modulation signal
    sum = 0
    for idx in range(samples_cnt):
        sum = sum + modulation_signal[idx]
        phase_components[idx] = sum
    # Calculate phase component caused by modulation signal
    phase_components = phase_components * frequency_sensitivity * sampling_period

    fm_signal = carrier_amp * np.cos((time_vector * 2 * np.pi * carrier_freq) + phase_components)

    return [fm_signal , phase_components]

# This function to linear scale of the output signal at FM demodulator to the modulation signal
# The vect to be scaled to reference vector ref_vect
def scale_signal(ref_vect, vect, invert = False):
    if (True == invert):
        vect = -1 * vect
    minval = min(ref_vect)
    maxval = max(ref_vect)
    aver = np.average([max(vect), min(vect)])
    vect_centered = vect - aver
    scale_factor = (maxval - minval) / (max(vect_centered) - min(vect_centered))
    vect_scaled = vect_centered * scale_factor
    offset = np.average([minval, maxval])
    vect_output = vect_scaled + offset

    return (vect_output)

# ----- MAIN PROGRAM -----
# Create time vector
time_vector = np.linspace(0,t_observation, NUMBER_OF_SAMPLES + 1 )
# Generate modulation signals
modulation_signal = generate_modulation_signal(time_vector, FM1_MOD_FREQ_LIST, FM1_MOD_AMP_LIST)
# Generate final FM signal
[signal, phase_comps] = modulate_fm(time_vector, FM1_CARRIER_FREQ, FM1_AMPLITURE, FM1_FREQ_SENSITIVITY, modulation_signal)

# Create NFM demodulator object and initialize it
demodulator = DemodulatorNFM(SAMPLING_FREQUENCY, OVERSAMPLING_RATIO)
discriminator_delay = demodulator.init(DISCRIMINATOR_DELAY_RATIO,
                 FM1_CARRIER_FREQ,
                 sum(FM1_MOD_AMP_LIST),
                 FM1_FREQ_SENSITIVITY)

# Apply sample by sample to the demodulate_nfm method
out_signal = np.empty(len(signal))
for idx, sample in enumerate(signal):
    out_signal[idx] = demodulator.demodulate_nfm(sample)

# Just apply linear scaling to the output signal to be able to plot modulation signal
# at the same plot as demodulated signal.
if (DISCRIMINATOR_DELAY_RATIO % 2):
    invert = False
else:
    invert = True
scaled_output = scale_signal(modulation_signal[CUT_SAMPLES_CNT:], out_signal[CUT_SAMPLES_CNT:], invert)

plt.figure()
plt.plot(modulation_signal)
plt.title("Modulation Signal")
plt.grid()

plt.figure()
plt.plot(out_signal[CUT_SAMPLES_CNT:])
plt.title("Demodulator Output")
plt.grid()

plt.figure()
plt.plot(modulation_signal[CUT_SAMPLES_CNT:], "--b")
plt.plot(scaled_output[discriminator_delay:], "r")
plt.title("Modulation Signal and Scaled Output Signal")
plt.grid()

plt.show()