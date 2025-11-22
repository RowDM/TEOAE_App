# 🩺 Portable TEOAE Measurement System

> **A Cross-Platform Medical IoT Device for Hearing Screening**

![Flutter](https://img.shields.io/badge/Flutter-3.0-blue) ![Python](https://img.shields.io/badge/Python-3.9-yellow) ![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Windows-lightgrey)

## 📖 Project Overview
This project implements a portable system for measuring **Transient Evoked Otoacoustic Emissions (TEOAE)**. It separates the heavy signal processing (Python/PC) from the user interface (Android/Flutter), creating a "Wireless Medical Controller" experience.

The system generates non-linear click stimuli, records the ear's response, and visualizes the otoacoustic emission waveform in real-time.

## 🏥 Key Features
* **Real-time Waveform Visualization:**
    * **Oscilloscope Mode:** Displays sine waves during calibration.
    * **Spectrum Mode:** Displays FFT (Frequency vs dB SPL) during TEOAE testing.
* **3-Step Clinical Workflow:**
    1.  **Calibration:** Microphone sensitivity correction (94dB SPL reference).
    2.  **Verification:** Speaker output check (1kHz Tone).
    3.  **Measurement:** Full TEOAE non-linear extraction.
* **IoT Architecture:** Low-latency communication via HTTP/REST over local Wi-Fi.
* **Smart Data:** Validates hardware IDs (e.g., "2- USB Audio Device") for stability.

---

## ⚙️ System Architecture
The system consists of two parts working in tandem:

1.  **The "Brain" (Python Backend):** Runs on a laptop connected to the USB Audio Interface. It handles the physics, audio drivers, and mathematical processing.
2.  **The "Remote" (Flutter App):** Runs on an Android phone. It sends commands and displays the results/graphs.

```mermaid
graph LR
    A[Android Phone] -- HTTP Request --> B(Laptop / Python Server)
    B -- Audio Out --> C[Ear Probe Speaker]
    C -- Sound --> D[Human Ear]
    D -- Echo --> C
    C -- Audio In --> B
    B -- JSON Data + Waveform --> A
