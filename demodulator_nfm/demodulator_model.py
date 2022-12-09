
import numpy as np
import matplotlib.pyplot as plt

# =========== USER DEFINES =============
RECEIVER_SAMPLING_FREQUENCY = 100.0e3                     # Hz - Frequency of local oscillator
OVERSAMPLING_RATIO = 4 * 1
SAMPLING_FREQUENCY = OVERSAMPLING_RATIO * RECEIVER_SAMPLING_FREQUENCY  # Hz - ADC sampling frequency
DISCRIMINATOR_DELAY_RATIO = 9


# Parameters of modulation signal:
FM1_CARRIER_FREQ = 147.1e3   # Hz - Carrier frequency of FM signal
FM1_AMPLITURE = 1            # units - Amplitude of carrier frequency in FM signal
FM1_FREQ_SENSITIVITY = 1000  #  - frequency sensitivity [ Hz/V ]
# List of frequency components in modulation signal
FM1_MOD_FREQ_LIST = [1040, 1490] # Hz
# List of amplitudes of frequency components in modulation signal
FM1_MOD_AMP_LIST =  [0.6,  0.4 ] # units - does not matter in the model (e.g. Volts or Amperes)

NUMBER_OF_SAMPLES = 4000     # Number of samples for simulation
CUT_SAMPLES_CNT = 150        # Number of samples at the beginning to skip transient process caused by IIR DF

# Calculate delay in polar discriminator and round it to integer
DISCRIMINATOR_DELAY_PRECISE = \
    DISCRIMINATOR_DELAY_RATIO * SAMPLING_FREQUENCY / (2 * abs(RECEIVER_SAMPLING_FREQUENCY - FM1_CARRIER_FREQ))    # Samples - Delay in polar frequency discriminator
DISCRIMINATOR_DELAY = round(DISCRIMINATOR_DELAY_PRECISE)

max_phase_deviation = FM1_FREQ_SENSITIVITY * (DISCRIMINATOR_DELAY / SAMPLING_FREQUENCY) * (sum(FM1_MOD_AMP_LIST))

# Digital Filter coefficients
# LPF, IIR, Order 1. Pass band 0.01*fs, Stop band 0.1*fs, attenuation in stop band -20dB.
# Numerator coefficients
# DF_BCOEF = [ 0.03054, 0.03054 ]
# # Denumerator coefficients
# DF_ACOEF = [ 1.0, -0.9389]

# LPF, IIR, Order 1. Pass band 0.1*fs, Stop band 0.35*fs, attenuation in stop band -20dB.
# Numerator coefficients
DF_BCOEF = [0.1584, 0.1584]
# Denumerator coefficients
DF_ACOEF = [1.0, -0.6832]
# =========== USER DEFINES (end) =============

# Buffers to store digital filter internal data
global DF_Buffer_I_Input
global DF_Buffer_I_Output
global DF_Buffer_Q_Input
global DF_Buffer_Q_Output
DF_Buffer_I_Input = 0
DF_Buffer_I_Output = 0
DF_Buffer_Q_Input = 0
DF_Buffer_Q_Output = 0

# Precalculation
t_sampling = 1/SAMPLING_FREQUENCY
t_observation = t_sampling * (NUMBER_OF_SAMPLES)
print(f'Observation interval = {t_observation * 1e6} us')
print(f'Sampling period = {t_sampling * 1e6} us')
print(f'DISCRIMINATOR_DELAY = {DISCRIMINATOR_DELAY}')
print(f'DISCRIMINATOR_DELAY_PRECISE = {DISCRIMINATOR_DELAY_PRECISE}')
print(f'max_phase_dev = {max_phase_deviation} Hz * s = {max_phase_deviation * 360} deg')

# This function implements first order IIR digital filter.
# It processes one sample per one call.
# This function appointed for I components only.
def DigitalFilter_I_ProcessOneSample(NewSample):
    global DF_Buffer_I_Input
    global DF_Buffer_I_Output
    tmp = NewSample * DF_BCOEF[0]
    Accumulator = tmp + DF_Buffer_I_Input - (DF_Buffer_I_Output * DF_ACOEF[1])
    DF_Buffer_I_Input = NewSample * DF_BCOEF[1]
    DF_Buffer_I_Output = Accumulator
    return (Accumulator)
# Same function as previous but appointed for Q components
def DigitalFilter_Q_ProcessOneSample(NewSample):
    global DF_Buffer_Q_Input
    global DF_Buffer_Q_Output
    tmp = NewSample * DF_BCOEF[0]
    Accumulator = tmp + DF_Buffer_Q_Input - (DF_Buffer_Q_Output * DF_ACOEF[1])
    DF_Buffer_Q_Input = NewSample * DF_BCOEF[1]
    DF_Buffer_Q_Output = Accumulator
    return (Accumulator)

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

# # Create IQ components using multiplication by sin and cos
# def adc_iq(receiver_sampling_freq, sampling_freq, samples):
#     sampling_period = 1 / sampling_freq
#     samples_len = len(samples)
#     i_vect = np.empty(samples_len)
#     q_vect = np.empty(samples_len)
#     iq_vect = np.empty(samples_len, dtype=np.complex)
#     for idx, sample in enumerate(samples):
#         i_vect[idx] = samples[idx] * np.sin(2 * np.pi * receiver_sampling_freq * idx * sampling_period)
#         q_vect[idx] = samples[idx] * np.cos(2 * np.pi * receiver_sampling_freq * idx * sampling_period)
#         iq_vect[idx] = complex( i_vect[idx], q_vect[idx] )
#
#     return [iq_vect, i_vect, q_vect]

# Create IQ components using multiplication by
def adc_iq_simple(receiver_sampling_freq, sampling_freq, samples):
    samples_len = len(samples)
    i_vect = np.empty(samples_len)
    q_vect = np.empty(samples_len)
    iq_vect = np.empty(samples_len, dtype=np.complex)
    local_osc_period = int(sampling_freq / receiver_sampling_freq)
    local_osc_quaterperiod = int(local_osc_period / 4)
    sin_base = np.concatenate((np.ones(2 * local_osc_quaterperiod), -1 * np.ones(2 * local_osc_quaterperiod)))
    cos_base = np.concatenate((np.ones(local_osc_quaterperiod), -1 * np.ones(2 * local_osc_quaterperiod), np.ones(local_osc_quaterperiod)))
    for idx, sample in enumerate(samples):
        i_vect[idx] = samples[idx] * sin_base[idx % local_osc_period]
        q_vect[idx] = samples[idx] * cos_base[idx % local_osc_period]
        iq_vect[idx] = complex( i_vect[idx], q_vect[idx] )

    return [iq_vect, i_vect, q_vect]

def apply_pfd_simple(i_vect, q_vect, offset):
    samples_to_process = len(i_vect) - offset
    re_vect = np.empty(samples_to_process)
    im_vect = np.empty(samples_to_process)
    for idx in range(samples_to_process):
        re_vect[idx] = (i_vect[idx] * i_vect[idx + offset]) + (q_vect[idx] * q_vect[idx + offset])
        im_vect[idx] = (i_vect[idx] * q_vect[idx + offset]) - (q_vect[idx] * i_vect[idx + offset])

    return ([re_vect, im_vect])

# Apply LPF IIR filters to the IQ samples
def apply_lpf_iir(i_samples, q_samples):
    samples_len = len(i_samples)
    iq_vect = np.empty(samples_len, dtype=np.complex)
    i_samples_out = np.empty(samples_len)
    q_samples_out = np.empty(samples_len)
    for idx in range(samples_len):
        i_samples_out[idx] = DigitalFilter_I_ProcessOneSample(i_samples[idx])
        q_samples_out[idx] = DigitalFilter_Q_ProcessOneSample(q_samples[idx])
        iq_vect[idx] = complex(i_samples_out[idx], q_samples_out[idx])

    return [iq_vect, i_samples_out, q_samples_out]

# This function to linearly scale output signal at FM demodulator to the input signal
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
# Generate modulation signals using modulation_dict
modulation_signal = generate_modulation_signal(time_vector, FM1_MOD_FREQ_LIST, FM1_MOD_AMP_LIST)
# Generate final FM signal
[fm1, phase_comps] = modulate_fm(time_vector, FM1_CARRIER_FREQ, FM1_AMPLITURE, FM1_FREQ_SENSITIVITY, modulation_signal)

signal = fm1

# Multiply input signal samples by local oscillator
[iq_vect, i_vect, q_vect] = adc_iq_simple(RECEIVER_SAMPLING_FREQUENCY, SAMPLING_FREQUENCY, signal)
# Apply LPF to products and obtain I and Q components
[iq_vect, i_vect, q_vect] = apply_lpf_iir(i_vect, q_vect)

# Apply simplified version of polar frequency discriminator
[pfd_v2_re_vect, pfd_v2_im_vect]= apply_pfd_simple(i_vect, q_vect, DISCRIMINATOR_DELAY)

# # Apply LPF to the output of polar discriminator
[pfd_compl_filt, pfd_re_filt, pfd_im_filt] = apply_lpf_iir(pfd_v2_re_vect, pfd_v2_im_vect)

# Just apply linear scaling to the output signal to be able to plot modulation signal
# at the same plot as demodulated signal.
if (DISCRIMINATOR_DELAY_RATIO % 2):
    invert = True
else:
    invert = False
scaled_output = scale_signal(modulation_signal[CUT_SAMPLES_CNT:], pfd_im_filt[CUT_SAMPLES_CNT:], invert)

plt.figure()
plt.plot(modulation_signal[CUT_SAMPLES_CNT:])
plt.grid()
plt.title("modulating signal ")

# plt.figure()
# plt.plot(signal)
# plt.title("FM signal")
#
# plt.figure()
# plt.plot(phase_comps)
# plt.title("phase component of FM signal")

plt.figure()
plt.plot(i_vect, "b")
plt.plot(q_vect,"r")
plt.title("I and Q components")
#
plt.figure()
plt.plot(pfd_v2_re_vect, "b")
plt.plot(pfd_v2_im_vect, "r")
plt.grid()
plt.title("Re and Im after PFD")

# plt.figure()
# plt.plot(np.angle(pfd_compl_filt, deg = True))
# plt.grid()
# plt.title("angle")

plt.figure()
plt.plot(modulation_signal[CUT_SAMPLES_CNT:], "--b")
plt.plot(scaled_output, "r")
plt.title("Modulation Signal and Scaled Output Signal")
plt.grid()

plt.show()