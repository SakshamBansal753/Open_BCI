from pylsl import StreamInlet, resolve_streams
import time

print("\nSearching EEG stream...\n")

streams = resolve_streams()

for s in streams:

    print("FOUND:")
    print("Name:", s.name())
    print("Type:", s.type())
    print("Channels:", s.channel_count())
    print("-" * 40)

# ==========================================
# CONNECT EEG
# ==========================================

eeg_streams = [
    s for s in streams
    if s.name() == "obci_eeg1"
]

if len(eeg_streams) == 0:

    print("No EEG stream found")
    exit()

inlet = StreamInlet(eeg_streams[0])

print("\nConnected to EEG stream")

# ==========================================
# COUNT SAMPLES
# ==========================================

print("\nMeasuring sampling rate for 10 seconds...\n")

sample_count = 0

start = time.time()

while time.time() - start < 10:

    samples, timestamps = inlet.pull_chunk(timeout=1.0)

    sample_count += len(samples)

duration = time.time() - start

sampling_rate = sample_count / duration

print("\n===================================")
print("TOTAL SAMPLES :", sample_count)
print("DURATION      :", round(duration, 2))
print("SAMPLING RATE :", round(sampling_rate, 2), "Hz")
print("===================================\n")