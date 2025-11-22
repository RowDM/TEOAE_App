import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import datetime
import os

# ============================
# MIC CALIBRATION SETTINGS
# ============================
fs = 48000
duration = 5
target_freq = 1000
calibrator_level = 94.0         # 94 dB SPL calibrator
latency_samples = 2000

# USB probe microphone:
mic_device_index = 26

# ============================
# FUNCTIONS
# ============================

def record_calibration_tone():
    print("\nRecording calibration tone...")
    data = sd.rec(int(duration * fs),
                  samplerate=fs,
                  device=mic_device_index,
                  channels=1,
                  dtype='float32',
                  blocking=True)
    data = data.flatten()
    data = data[latency_samples:]  # remove device latency
    return data

def compute_fft_level(signal):
    N = len(signal)
    freqs = np.fft.rfftfreq(N, 1/fs)
    spectrum = np.fft.rfft(signal)
    ref = 20e-6  # 20 µPa
    dB = 20*np.log10(np.abs(spectrum) / ref * 2 / N)
    return freqs, dB

def get_calibration_value(freqs, dB_spectrum):
    idx = np.argmin(np.abs(freqs - target_freq))
    measured = dB_spectrum[idx]
    correction = calibrator_level - measured
    print(f"\nMeasured Mic Level @ 1 kHz = {measured:.2f} dB SPL")
    print(f"Calibration Correction Needed = {correction:.2f} dB")
    return correction

def save_calibration(correction, fname="mic_calibration.txt"):
    """Always update calibration file, creating it if needed."""
    # Optional: backup previous file
    if os.path.exists(fname):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{fname.replace('.txt','')}_backup_{timestamp}.txt"
        os.rename(fname, backup_name)
        print(f"Backed up previous calibration to {backup_name}")

    # Save new calibration
    with open(fname, "w") as f:
        f.write(str(correction))
    print(f"Saved updated calibration to {fname}")

# ============================
# MAIN
# ============================

def main():
    signal = record_calibration_tone()
    freqs, dB_spectrum = compute_fft_level(signal)
    correction = get_calibration_value(freqs, dB_spectrum)

    plt.figure(figsize=(10,5))
    plt.plot(freqs, dB_spectrum)
    plt.xlim([0, 3000])
    plt.title("Mic Calibration Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("dB SPL (uncalibrated)")
    plt.axvline(target_freq, color='r', linestyle='--')
    plt.show()

    save_calibration(correction)

if __name__ == "__main__":
    main()
