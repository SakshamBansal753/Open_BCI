from pylsl import StreamInlet, resolve_stream
import pandas as pd

# =====================================================
# SETTINGS
# =====================================================

EEG_STREAM_NAME = "obci_eeg1"

MARKER_STREAM_NAME = "markers"

# =====================================================
# CONNECT EEG
# =====================================================

print("\nConnecting EEG stream...\n")

eeg_stream = resolve_stream(
    'name',
    EEG_STREAM_NAME
)[0]

eeg_inlet = StreamInlet(eeg_stream)

print("EEG connected")

# =====================================================
# CONNECT MARKERS
# =====================================================

marker_stream = resolve_stream(
    'name',
    MARKER_STREAM_NAME
)[0]

marker_inlet = StreamInlet(marker_stream)

print("Markers connected")

# =====================================================
# STORAGE
# =====================================================

eeg_rows = []

marker_rows = []

recording_active = False

running = True

# =====================================================
# MAIN LOOP
# =====================================================

while running:

    # -------------------------------------------------
    # READ MARKERS
    # -------------------------------------------------

    markers, marker_ts = marker_inlet.pull_chunk(
        timeout=0.0
    )

    if marker_ts:

        for m, ts in zip(markers, marker_ts):

            marker = m[0]

            print(marker)

            marker_rows.append({

                "timestamp": ts,
                "marker": marker

            })

            if marker == "SESSION_START":

                recording_active = True

            elif marker == "SESSION_END":

                running = False

    # -------------------------------------------------
    # RECORD EEG
    # -------------------------------------------------

    if recording_active:

        samples, timestamps = eeg_inlet.pull_chunk(

            timeout=1.0,

            max_samples=128

        )

        if timestamps:

            for sample, ts in zip(samples, timestamps):

                row = {

                    "timestamp": ts

                }

                # SAVE ALL CHANNELS

                for ch in range(len(sample)):

                    row[f"CH{ch+1}"] = sample[ch]

                eeg_rows.append(row)

# =====================================================
# SAVE
# =====================================================

eeg_df = pd.DataFrame(eeg_rows)

marker_df = pd.DataFrame(marker_rows)

eeg_df.to_csv(
    "raw_eeg.csv",
    index=False
)

marker_df.to_csv(
    "markers.csv",
    index=False
)

# =====================================================
# STATS
# =====================================================

duration = (

    eeg_df["timestamp"].iloc[-1]

    -

    eeg_df["timestamp"].iloc[0]

)

print("\n===================================")

print("EEG Rows:", len(eeg_df))

print("Duration:",
      round(duration, 3))

print("Estimated Hz:",
      round(len(eeg_df)/duration, 2))

print("Channels:",
      len(eeg_df.columns)-1)

print("===================================\n")