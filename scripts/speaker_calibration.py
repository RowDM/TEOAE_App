import numpy as np
from scipy.io import savemat
import datetime
import matplotlib.pyplot as plt
import sounddevice as sd
import os

plt.close('all')

# =============================
# SETTINGS
# =============================
fsamp = 48000
latency_samples = 2125
f_tone = 1000
duration = 1

# digital amplitude (not SPL-related)
stim_amp = 0.5

mic_correction_file = "mic_calibration.txt"

# =============================
# DEVICES
# =============================
mic_device = 26
speaker_device = 25
device_pair = (mic_device, speaker_device)

# =============================
def get_time():
    return datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

def load_mic_correction(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            correction = float(f.read())
        print(f"Loaded mic calibration: {correction:.2f} dB")
        return correction
    else:
        print("Mic calibration file not found. Using 0 dB correction.")
        return 0.0

def generate_tone():
    t = np.arange(0, duration, 1/fsamp)
    tone = stim_amp * np.sin(2*np.pi*f_tone*t)
    tone = np.pad(tone, (latency_samples,0), 'constant')
    return tone.astype('float32').reshape(-1,1)

def compute_fft_level(signal):
    N = len(signal)
    freqs = np.fft.rfftfreq(N, 1/fsamp)
    spec = np.fft.rfft(signal)
    ref = 20e-6
    dB = 20*np.log10(np.abs(spec)/ref * 2/N)
    return freqs, dB

# =============================
# MAIN
# =============================
mic_correction = load_mic_correction(mic_correction_file)

subject = "88"
save_folder = f"C:/TEOAE_raw/{subject}"
os.makedirs(save_folder, exist_ok=True)

stimulus = generate_tone()

recorded = sd.playrec(
    stimulus,
    samplerate=fsamp,
    device=device_pair,
    channels=1,
    dtype='float32',
    blocking=True
)

signal = recorded.flatten()

# === SPL ===
rms_pa = np.sqrt(np.mean(signal**2))
spl_raw = 20*np.log10(rms_pa / 20e-6)
spl_corrected = spl_raw + mic_correction

print(f"Measured SPL: {spl_raw:.2f} dB")
print(f"Corrected SPL: {spl_corrected:.2f} dB")

freqs, dB = compute_fft_level(signal)
dB_corrected = dB + mic_correction

plt.figure()
plt.plot(freqs, dB_corrected)
plt.xlim([0,5000])
plt.title("Speaker Output Test (Corrected SPL)")
plt.xlabel("Hz")
plt.ylabel("dB SPL")
plt.grid()
plt.show()

print("\nSpeaker calibration complete.")
