import sys
import serial
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import numpy as np

# --- Settings ---
PORT = 'COM3'
BAUD_RATE = 921600
WINDOW_SIZE = 1000  
SAMPLING_RATE = 10000 
V_REF = 3.3

class ProDSO(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"ESP32 Professional DSO - {PORT}")
        self.resize(1100, 600)
        self.is_running = True

        # Main Layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QHBoxLayout(self.central_widget)

        # Plot Area
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setYRange(0, V_REF + 0.1)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.curve = self.plot_widget.plot(pen=pg.mkPen('y', width=2))
        self.layout.addWidget(self.plot_widget, stretch=4)

        # Control Panel Area
        self.panel = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.panel, stretch=1)

        self.btn_stop = QtWidgets.QPushButton("STOP")
        self.btn_stop.setStyleSheet("background-color: #900; color: white; font-weight: bold; height: 50px;")
        self.btn_stop.clicked.connect(self.toggle_run)
        self.panel.addWidget(self.btn_stop)

        # --- UPDATED: Added Amplitude Label ---
        self.lbl_vpp = QtWidgets.QLabel("Vpp: 0.00 V")
        self.lbl_amp = QtWidgets.QLabel("Amp: 0.00 V") 
        self.lbl_freq = QtWidgets.QLabel("Freq: 0 Hz")
        
        for lbl in [self.lbl_vpp, self.lbl_amp, self.lbl_freq]:
            lbl.setStyleSheet("font-size: 18px; color: #0f0; font-family: monospace; background: #222; padding: 10px;")
            self.panel.addWidget(lbl)
        
        self.panel.addStretch()

        # Data & Trigger State
        self.data_buffer = np.zeros(WINDOW_SIZE)
        self.trigger_level = V_REF / 2.0  # Trigger at 1.65V
        self.is_capturing = False
        self.capture_index = 0
        self.waiting_for_low = True 
        self.vpp_history = []
        
        # Serial Init
        try:
            self.ser = serial.Serial(PORT, BAUD_RATE, timeout=0.1)
        except Exception as e:
            print(f"Error: {e}")
            self.ser = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_logic)
        self.timer.start(0)

    def toggle_run(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.btn_stop.setText("STOP")
            self.btn_stop.setStyleSheet("background-color: #900;")
        else:
            self.btn_stop.setText("RUN")
            self.btn_stop.setStyleSheet("background-color: #090;")

    def calculate_measurements(self, data):
        # 1. Moving Average Vpp
        raw_vpp = np.max(data) - np.min(data)
        self.vpp_history.append(raw_vpp)
        if len(self.vpp_history) > 5:
            self.vpp_history.pop(0)
            
        avg_vpp = np.mean(self.vpp_history)
        self.lbl_vpp.setText(f"Vpp: {avg_vpp:.2f} V")

        # --- NEW: Amplitude (Peak Voltage) Math ---
        # Amplitude is exactly half of the Peak-to-Peak voltage
        avg_amp = avg_vpp / 2.0
        self.lbl_amp.setText(f"Amp: {avg_amp:.2f} V")

        # 2. Schmitt Trigger Frequency Math
        if avg_vpp < 0.1:
            self.lbl_freq.setText("Freq: 0 Hz")
            return

        centered = data - np.mean(data)
        noise_margin = avg_vpp * 0.05 
        
        crossings = []
        is_high = centered[0] > 0
        
        for i in range(1, len(centered)):
            if not is_high and centered[i] > noise_margin:
                crossings.append(i)
                is_high = True
            elif is_high and centered[i] < -noise_margin:
                is_high = False
                
        if len(crossings) >= 2:
            avg_period = np.mean(np.diff(crossings))
            freq = SAMPLING_RATE / avg_period
            self.lbl_freq.setText(f"Freq: {int(freq)} Hz")
        else:
            self.lbl_freq.setText("Freq: < 10 Hz")

    def update_logic(self):
        if not self.is_running or not self.ser:
            return

        lines_processed = 0
        while self.ser.in_waiting > 0 and lines_processed < 2000:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if not line.isdigit():
                    continue
                    
                val = (int(line) / 4095.0) * V_REF
                
                # State 1: Wait for Trigger
                if not self.is_capturing:
                    if val < self.trigger_level:
                        self.waiting_for_low = False
                    elif not self.waiting_for_low and val >= self.trigger_level:
                        self.is_capturing = True
                        self.capture_index = 0
                        self.waiting_for_low = True

                # State 2: Capture Full Buffer
                if self.is_capturing:
                    self.data_buffer[self.capture_index] = val
                    self.capture_index += 1
                    
                    # State 3: Draw Once Per Frame
                    if self.capture_index >= WINDOW_SIZE:
                        self.curve.setData(self.data_buffer)
                        self.calculate_measurements(self.data_buffer)
                        self.is_capturing = False
                        break 
                        
            except Exception:
                pass 
            
            lines_processed += 1

if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    win = ProDSO()
    win.show() 
    sys.exit(app.exec_())