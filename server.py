from flask import Flask, jsonify
import numpy as np
import sounddevice as sd

app = Flask(__name__)

# ==========================================
# GLOBAL STATE
# ==========================================
CURRENT_MIC_CORRECTION = 108.28 

# DEVICE CONFIG (Update these IDs if needed!)
fs = 48000
mic_device = 27
speaker_device = 26
device_pair = (mic_device, speaker_device)

# ==========================================
# HELPERS
# ==========================================
def calculate_db_spl(signal):
    rms = np.sqrt(np.mean(signal**2))
    if rms == 0: return 0
    return 20 * np.log10(rms / 20e-6)

def generate_tone(fs, duration, freq, amp, latency_samples):
    t = np.arange(0, duration, 1/fs)
    tone = amp * np.sin(2*np.pi*freq*t)
    return np.pad(tone, (latency_samples, 0), 'constant').astype(np.float32).reshape(-1, 1)

def generate_chirp(fs, duration, f_start, f_end, dB_level, latency_samples):
    t = np.arange(0, duration, 1/fs)
    amp = 10**(dB_level/20) * np.sqrt(2) * 2e-5  
    k = np.log(f_end / f_start) / duration
    phase = 2 * np.pi * f_start * (np.exp(k * t) - 1) / k
    chirp = amp * np.sin(phase)
    return np.pad(chirp, (latency_samples, 0), 'constant').astype(np.float32).reshape(-1, 1)

# ==========================================
# ROUTES
# ==========================================

@app.route('/step1_calibrate_mic', methods=['GET'])
def calibrate_mic():
    global CURRENT_MIC_CORRECTION
    try:
        print("--- Step 1: Mic Calibration ---")
        duration = 3.0 
        # Record 3 seconds of the Calibrator Tone
        recording = sd.rec(int(duration * fs), samplerate=fs, device=mic_device, channels=1, dtype='float32', blocking=True)
        flat_rec = recording.flatten()
        
        # Calc dB
        raw_db = calculate_db_spl(flat_rec)
        CURRENT_MIC_CORRECTION = 94.0 - raw_db
        
        # VISUALIZATION: Take a 50ms slice (2400 samples) from the middle
        # We skip the first 4000 samples to avoid any startup "pop" or silence
        viz_slice = flat_rec[4000:6400].tolist()

        return jsonify({
            "status": "success", 
            "value": f"{CURRENT_MIC_CORRECTION:.2f}", 
            "message": "Mic Calibrated!",
            "data": viz_slice # <--- Sending the Sine Wave for the Graph
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/step2_check_speaker', methods=['GET'])
def check_speaker():
    try:
        print("--- Step 2: Speaker Check ---")
        stim_amp = 0.001 
        tone = generate_tone(fs, 1.0, 1000, stim_amp, 2125)
        
        # Play & Record
        recorded = sd.playrec(tone, samplerate=fs, device=device_pair, channels=1, dtype='float32', blocking=True)
        flat_rec = recorded.flatten()
        
        # Calc dB
        raw_db = calculate_db_spl(flat_rec)
        final_db = raw_db + CURRENT_MIC_CORRECTION
        
        # VISUALIZATION: Take 50ms slice where the tone is playing
        # Skip latency (2125) + a bit more to be safe
        start_idx = 3000
        viz_slice = flat_rec[start_idx : start_idx + 2400].tolist()
        
        return jsonify({
            "status": "success", 
            "value": f"{final_db:.2f}", 
            "message": "Speaker OK",
            "data": viz_slice # <--- Sending Speaker Tone for the Graph
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/step3_run_teoae', methods=['GET'])
def run_teoae():
    try:
        print("--- Step 3: TEOAE Test ---")
        chirp = generate_chirp(fs, 0.02, 500, 6000, 60, 2125)
        stimulus = np.vstack([chirp, -chirp, -chirp, chirp])
        
        recorded = sd.playrec(stimulus, samplerate=fs, device=device_pair, channels=1, dtype='float32', blocking=True)
        flat_rec = recorded.flatten()
        
        # Nonlinear Processing
        N = len(chirp)
        P1, P2, P3, P4 = flat_rec[0:N], flat_rec[N:2*N], flat_rec[2*N:3*N], flat_rec[3*N:4*N]
        nonlinear = P1 - P2 - P3 + P4
        
        raw_db = calculate_db_spl(nonlinear)
        final_db = raw_db + CURRENT_MIC_CORRECTION
        
        # VISUALIZATION: The full nonlinear response is short enough (~2000 samples), so send it all
        waveform_data = nonlinear.tolist()

        print(f"Result: {final_db:.2f} dB")
        return jsonify({
            "status": "success", 
            "value": f"{final_db:.2f}", 
            "message": "Test Complete",
            "data": waveform_data 
        })
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)