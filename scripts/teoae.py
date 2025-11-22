import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.io import savemat
import datetime
import os

# =============================
# Settings for your TEOAE system
# =============================
fs = 48000                   # Sampling rate
duration_chirp = 0.02        # Chirp duration in seconds (20 ms)
latency_samples = 2125       # Adjust latency based on your hardware (~44ms)
f_start = 500                # Chirp start frequency in Hz
f_end = 6000                 # Chirp end frequency in Hz
L = 60                       # Desired stimulus level in dB SPL
mic_correction = 108.28      # Your measured mic calibration correction in dB

# Devices (your confirmed devices)
mic_device = 29
speaker_device = 28
device_pair = (mic_device, speaker_device)

# Output folder
subject = "portable_TE"
save_folder = f"C:/TEOAE_raw/{subject}"
os.makedirs(save_folder, exist_ok=True)

# =============================
# Functions
# =============================

def get_time_str():
    return datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

def generate_chirp(fs, duration, f_start, f_end, dB_level, latency_samples):
    t = np.arange(0, duration, 1/fs)
    # Calculate amplitude from dB SPL
    amp = 10**(dB_level/20) * np.sqrt(2) * 2e-5  
    # Generate logarithmic chirp
    k = np.log(f_end / f_start) / duration
    instantaneous_phase = 2 * np.pi * f_start * (np.exp(k * t) - 1) / k
    chirp = amp * np.sin(instantaneous_phase)
    # Add latency padding
    chirp = np.pad(chirp, (latency_samples, 0), 'constant')
    return chirp.astype(np.float32).reshape(-1, 1)

def playrec(stimulus):
    return sd.playrec(stimulus, samplerate=fs, device=device_pair,
                      channels=1, dtype='float32', blocking=True)

def compute_fft_level(signal, fs):
    N = len(signal)
    spectrum = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(N, 1/fs)
    ref = 20e-6
    dB = 20 * np.log10(np.abs(spectrum) / ref * 2 / N)
    return freqs, dB

# =============================
# Generate 4-pulse nonlinear stimulus
# =============================
print("Generating 4-pulse nonlinear stimulus...")
# Generate one chirp stimulus
chirp = generate_chirp(fs, duration_chirp, f_start, f_end, L, latency_samples)

# Four pulses with nonlinear weighting (P1 - P2 - P3 + P4)
stimulus = np.vstack([
    chirp,
    -chirp,
    -chirp,
    chirp
])

print(f"Stimulus shape: {stimulus.shape}")

# =============================
# Play and record
# =============================
print("Playing stimulus and recording response...")
recorded = playrec(stimulus)

# Flatten the recorded data
recorded = recorded.flatten()

# =============================
# Nonlinear TEOAE extraction
# =============================
N = len(chirp)
P1 = recorded[0*N:1*N]
P2 = recorded[1*N:2*N]
P3 = recorded[2*N:3*N]
P4 = recorded[3*N:4*N]

nonlinear_response = P1 - P2 - P3 + P4

# =============================
# RMS and SPL calculation
# =============================
rms_pa = np.sqrt(np.mean(nonlinear_response**2))
spl_measured = 20 * np.log10(rms_pa / 20e-6)
spl_corrected = spl_measured + mic_correction

print(f"Nonlinear response RMS SPL (uncorrected): {spl_measured:.2f} dB SPL")
print(f"Nonlinear response RMS SPL (corrected): {spl_corrected:.2f} dB SPL")

# =============================
# Plotting
# =============================
plt.figure(figsize=(12,6))
plt.plot(nonlinear_response)
plt.title('Nonlinear TEOAE Response (Time Domain)')
plt.xlabel('Samples')
plt.ylabel('Amplitude')
plt.grid(True)
plt.show()

# FFT plot
freqs, dB = compute_fft_level(nonlinear_response, fs)
dB_corrected = dB + mic_correction

plt.figure(figsize=(12,6))
plt.plot(freqs, dB_corrected)
plt.title('Nonlinear TEOAE Response (Frequency Domain, Corrected SPL)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('dB SPL')
plt.xlim(0, 8000)
plt.grid(True)
plt.show()

# =============================
# Save data
# =============================
timestamp = get_time_str()
filename = f"TEOAE_nonlinear_{timestamp}.mat"
fullpath = os.path.join(save_folder, filename)

savemat(fullpath, {
    'nonlinear_response': nonlinear_response,
    'P1': P1,
    'P2': P2,
    'P3': P3,
    'P4': P4,
    'stimulus': stimulus.flatten(),
    'fs': fs,
    'mic_correction': mic_correction,
    'f_start': f_start,
    'f_end': f_end,
    'duration_chirp': duration_chirp
})

print(f"Saved TEOAE nonlinear response to: {fullpath}")
print("Portable TEOAE measurement complete.")
