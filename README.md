# Portable Digital Storage Oscilloscope (DSO)

A low-cost, DIY portable Digital Storage Oscilloscope (DSO) designed for students, hobbyists, and field use. This project bridges a hardware signal conditioning circuit with a custom Python-based graphical interface to provide real-time signal visualization and measurement, offering an affordable alternative to commercial DSOs for educational labs and circuit debugging.

## 🚀 Features

* **Real-Time Visualization:** Smooth, responsive waveform plotting using PyQtGraph on a PC monitor.
* **High-Speed Sampling:** Hardware timer-driven 10 kHz analog sampling using the ESP32's Internal RAM (IRAM) to prevent flash bottlenecks.
* **Automatic Measurements:** Live calculation and display of Amplitude (Amp), Peak-to-Peak Voltage (Vpp), and Frequency estimation.
* **Smart Triggering:** Software-based Schmitt Trigger logic stabilizes waveform capture for clean visualization.
* **Highly Portable:** Compact, affordable, and easy to build using standard components on a breadboard or custom PCB.

## 📁 Repository Structure

```text
├── Src/
|   └── esp32_dso.ino        # ESP32 C/C++ source code (Interrupt & ADC logic)
│   ├── python_dso.py            # Python host script (PyQtGraph GUI & serial parser)
│   └── requirements.txt         # Python dependencies
├── setup                        # hardware setup and flowchart
├── docs/                        
│   └── Portable_DSO_Presentation.pptx # Project presentation and  demo video
├── .gitignore                   # Git ignore file for Python environments and C++ builds
├── LICENSE                      # MIT License
└── README.md                    # Project documentation
