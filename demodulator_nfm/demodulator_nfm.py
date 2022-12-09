
import numpy as np

class DemodulatorNFM():

    def __init__(self, sampling_freq, oversampling_ratio):

        # Digital Filter coefficients
        # LPF, IIR, Order 1. Pass band 0.01*fs, Stop band 0.1*fs, attenuation in stop band -20dB.
        # Numerator coefficients
        # self.DF_BCOEF = [0.03054, 0.03054]
        # # Denumerator coefficients
        # self.DF_ACOEF = [1.0, -0.9389]

        # LPF, IIR, Order 1. Pass band 0.1*fs, Stop band 0.35*fs, attenuation in stop band -20dB.
        # Numerator coefficients
        self.DF_BCOEF = [0.1584, 0.1584]
        # Denumerator coefficients
        self.DF_ACOEF = [1.0, -0.6832]

        self.sampling_freq = sampling_freq
        self.localosc_sampling_freq = int(sampling_freq / oversampling_ratio)
        self.local_osc_period = int(sampling_freq / self.localosc_sampling_freq)
        local_osc_quarterperiod = int(self.local_osc_period / 4)
        self.sin_base = np.concatenate((np.ones(2 * local_osc_quarterperiod), -1 * np.ones(2 * local_osc_quarterperiod)))
        self.cos_base = np.concatenate((np.ones(local_osc_quarterperiod), -1 * np.ones(2 * local_osc_quarterperiod),
                                   np.ones(local_osc_quarterperiod)))
        print(f'sin base: {self.sin_base}')
        print(f'cos base: {self.cos_base}')


    def init(self,
             discriminator_delay_ratio,
             fm_carrier_frequency,
             fm_modulation_amplitude,
             fm_frequency_sensitivity):
        # Buffers to store digital filter internal data
        self.DF_Buffer_I_Input = 0
        self.DF_Buffer_I_Output = 0
        self.DF_Buffer_Q_Input = 0
        self.DF_Buffer_Q_Output = 0
        self.DF_Buffer_PolarOut_Input = 0
        self.DF_Buffer_PolarOut_Output = 0
        self.locosc_idx = 0

        # Calculate delay in polar discriminator and round it to integer
        discriminator_delay_precise = \
            discriminator_delay_ratio * self.sampling_freq / (2 * abs(
                self.localosc_sampling_freq - fm_carrier_frequency))  # Samples - Delay in polar frequency discriminator
        self.discriminator_delay = round(discriminator_delay_precise)

        max_phase_deviation = \
            fm_frequency_sensitivity * (self.discriminator_delay / self.sampling_freq) * (fm_modulation_amplitude)

        self.i_delay_buffer = np.zeros(self.discriminator_delay)
        self.q_delay_buffer = np.zeros(self.discriminator_delay)
        self.delay_buffer_idx = 0

        print(f'Discriminator delay in samples (precise): {discriminator_delay_precise}')
        print(f'Discriminator delay in samples (rounded): {self.discriminator_delay}')
        print(f'Max phase deviation: {max_phase_deviation} Hz * s = {max_phase_deviation * 360} deg')

        return self.discriminator_delay

    # This function uses the following global
    def demodulate_nfm(self, newsample):
        # multiply with local oscillator
        i_sample = newsample * self.sin_base[self.locosc_idx]
        q_sample = newsample * self.cos_base[self.locosc_idx]
        self.locosc_idx = (self.locosc_idx + 1) % self.local_osc_period

        # LPF I channel
        accumulator = i_sample * self.DF_BCOEF[0]
        accumulator = accumulator + self.DF_Buffer_I_Input - (self.DF_Buffer_I_Output * self.DF_ACOEF[1])
        self.DF_Buffer_I_Input = i_sample * self.DF_BCOEF[1]
        self.DF_Buffer_I_Output = accumulator
        i_sample = accumulator

        # LPF Q channel
        accumulator = q_sample * self.DF_BCOEF[0]
        accumulator = accumulator + self.DF_Buffer_Q_Input - (self.DF_Buffer_Q_Output * self.DF_ACOEF[1])
        self.DF_Buffer_Q_Input = q_sample * self.DF_BCOEF[1]
        self.DF_Buffer_Q_Output = accumulator
        q_sample = accumulator

        polar_det_out = (i_sample * self.q_delay_buffer[self.delay_buffer_idx]) -\
                        (q_sample * self.i_delay_buffer[self.delay_buffer_idx])
        self.i_delay_buffer[self.delay_buffer_idx] = i_sample
        self.q_delay_buffer[self.delay_buffer_idx] = q_sample
        self.delay_buffer_idx = (1 + self.delay_buffer_idx) % self.discriminator_delay

        # Apply LPF to polar discriminator output
        accumulator = polar_det_out * self.DF_BCOEF[0]
        accumulator = accumulator + self.DF_Buffer_PolarOut_Input - (self.DF_Buffer_PolarOut_Output * self.DF_ACOEF[1])
        self.DF_Buffer_PolarOut_Input = polar_det_out * self.DF_BCOEF[1]
        self.DF_Buffer_PolarOut_Output = accumulator
        OutputSample = accumulator

        return OutputSample