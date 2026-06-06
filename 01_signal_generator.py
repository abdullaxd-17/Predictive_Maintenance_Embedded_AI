# ============================================================
# FILE: jupyter/01_signal_generator.py
# TOOL: Jupyter Notebook (paste each section into a cell)
# HOW:  Run cell by cell. Cell 1 installs libs, Cell 2 defines
#       signal functions, Cell 3 opens serial and streams data.
# ============================================================

# ── CELL 1 ── Install dependencies (run once)
# !pip install numpy scipy pyserial matplotlib

# ── CELL 2 ── Imports & constants
import numpy as np
import scipy.signal as sig
import serial
import struct
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

FS   = 1000   # sampling rate Hz
N    = 128    # samples per window
t    = np.linspace(0, N/FS, N, endpoint=False)

LABELS = ["NORMAL", "BEARING", "IMBALANCE", "LOOSE", "OVERLOAD"]

# ── CELL 3 ── Signal generator functions
def gen_normal():
    """Healthy machine: low broadband noise only"""
    return np.random.normal(0, 0.05, N).astype(np.float32)

def gen_bearing():
    """Bearing fault: impulsive spikes at ball-pass frequency ~62.5 Hz"""
    impulse = np.zeros(N)
    impulse[::16] = 1.2                          # spike every 16 samples = 62.5 Hz
    env = np.convolve(impulse, np.hanning(5)/3, 'same')
    return (env + np.random.normal(0, 0.04, N)).astype(np.float32)

def gen_imbalance():
    """Mass imbalance: dominant 1x rotational at 25 Hz"""
    return (0.8 * np.sin(2*np.pi*25*t) + np.random.normal(0, 0.06, N)).astype(np.float32)

def gen_loose():
    """Loose mounting: sub-harmonic at 12.5 Hz + 25 Hz"""
    return (0.5*np.sin(2*np.pi*12.5*t) +
            0.3*np.sin(2*np.pi*25*t)   +
            np.random.normal(0, 0.07, N)).astype(np.float32)

def gen_overload():
    """Overload: high amplitude broadband + 50 Hz harmonic"""
    return (1.5*np.random.normal(0, 0.2, N) +
            0.4*np.sin(2*np.pi*50*t)).astype(np.float32)

GENERATORS = [gen_normal, gen_bearing, gen_imbalance, gen_loose, gen_overload]

# ── CELL 4 ── Preview all 5 signals (no hardware needed)
fig, axes = plt.subplots(5, 1, figsize=(12, 10), tight_layout=True)
fig.suptitle("Simulated Vibration Signals", fontsize=14, fontweight='bold')
colors = ['#22c55e','#ef4444','#f97316','#eab308','#dc2626']
for ax, fn, label, color in zip(axes, GENERATORS, LABELS, colors):
    data = fn()
    ax.plot(t*1000, data, color=color, linewidth=0.8)
    ax.set_ylabel(label, fontsize=9)
    ax.set_ylim(-2.5, 2.5)
    ax.grid(True, alpha=0.3)
axes[-1].set_xlabel("Time (ms)")
plt.savefig("signals_preview.png", dpi=150)
plt.show()
print("Signal preview saved as signals_preview.png")

# ── CELL 5 ── Serial frame sender
# CHANGE 'COM5' to your STM32 port:
#   Windows: 'COM3', 'COM4', 'COM5' etc  (check Device Manager)
#   Linux:   '/dev/ttyACM0' or '/dev/ttyUSB0'
#   Mac:     '/dev/cu.usbmodem...'

SERIAL_PORT = 'COM5'   # <-- CHANGE THIS
BAUD        = 115200

def send_window(ser, data):
    """Pack 128 float32 samples as: [0xAA][0xBB][len_low][len_high][...data...]"""
    payload = struct.pack(f'<{N}f', *data)              # 512 bytes little-endian
    header  = bytes([0xAA, 0xBB]) + struct.pack('<H', len(payload))
    ser.write(header + payload)

def send_and_receive(ser, fault_class):
    """Send one window, return STM32 JSON reply string"""
    fn    = GENERATORS[fault_class]
    data  = fn()
    send_window(ser, data)
    reply = ser.readline().decode('utf-8', errors='ignore').strip()
    return data, reply

# ── CELL 6 ── Run continuous stream (Ctrl+C to stop)
# Results are printed AND saved to results_log.txt for validation
print(f"Opening {SERIAL_PORT} at {BAUD} baud...")
ser = serial.Serial(SERIAL_PORT, BAUD, timeout=2)
time.sleep(2)   # wait for STM32 to enumerate
print("Connected. Cycling through fault classes...\n")

log = []
try:
    for cycle in range(50):               # 50 windows, ~150 seconds
        fault_idx = cycle % 5             # cycle NORMAL→BEARING→...→OVERLOAD
        data, reply = send_and_receive(ser, fault_idx)
        sent_label  = LABELS[fault_idx]
        print(f"[{cycle+1:02d}] Sent: {sent_label:10s}  STM32 reply: {reply}")
        log.append({"sent": sent_label, "reply": reply, "ts": time.time()})
        time.sleep(3)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    ser.close()

# Save log
import json
with open("results_log.json", "w") as f:
    json.dump(log, f, indent=2)
print(f"\nLog saved: {len(log)} entries → results_log.json")

# ── CELL 7 ── (Optional) Interactive mode: press key to choose fault
# Run this cell for a manual demo
import sys
print("Keys: 1=NORMAL  2=BEARING  3=IMBALANCE  4=LOOSE  5=OVERLOAD  q=quit")
ser = serial.Serial(SERIAL_PORT, BAUD, timeout=2)
time.sleep(2)
while True:
    key = input("Fault class (1-5, q): ").strip()
    if key == 'q': break
    if key in '12345':
        idx = int(key) - 1
        data, reply = send_and_receive(ser, idx)
        print(f"  Sent: {LABELS[idx]}  →  STM32: {reply}")
ser.close()
