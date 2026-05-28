# =====================================================
# synchronize.py
# EEG + MARKER ALIGNMENT
# ROBUST MOTOR IMAGERY SYNCHRONIZATION
# =====================================================

import pandas as pd

# =====================================================
# SETTINGS
# =====================================================

EXPECTED_HZ = 250

EXPECTED_DT = 1 / EXPECTED_HZ

# packet discontinuity threshold
LOSS_THRESHOLD = EXPECTED_DT * 4

# rolling continuity window
ROLLING_WINDOW = 5

# invalidate surrounding rows
INVALID_WINDOW = 25

# =====================================================
# LOAD FILES
# =====================================================

print("\nLoading files...\n")

eeg_df = pd.read_csv(
    "raw.csv"
)

marker_df = pd.read_csv(
    "mark.csv"
)

# =====================================================
# CHECK EMPTY
# =====================================================

if len(eeg_df) == 0:

    print("\nERROR: EEG FILE EMPTY\n")

    exit()

if len(marker_df) == 0:

    print("\nERROR: MARKER FILE EMPTY\n")

    exit()

# =====================================================
# SORT
# =====================================================

eeg_df = eeg_df.sort_values(
    "timestamp"
).reset_index(drop=True)

marker_df = marker_df.sort_values(
    "timestamp"
).reset_index(drop=True)

# =====================================================
# INITIALIZE LABELS
# =====================================================

eeg_df["label"] = "NO_LABEL"

eeg_df["validity"] = "VALID"

# =====================================================
# TIMESTAMP DIFFERENCE
# =====================================================

eeg_df["dt"] = eeg_df["timestamp"].diff()

# =====================================================
# ROLLING CONTINUITY
# =====================================================

eeg_df["rolling_dt"] = (

    eeg_df["dt"]

    .rolling(
        ROLLING_WINDOW,
        center=True
    )

    .mean()

)

# =====================================================
# PACKET LOSS DETECTION
# =====================================================

eeg_df["packet_loss"] = (

    eeg_df["rolling_dt"]

    > LOSS_THRESHOLD

)

loss_indices = eeg_df.index[
    eeg_df["packet_loss"]
].tolist()

print("\nDetected discontinuities:",
      len(loss_indices))

# =====================================================
# APPLY LABELS
# =====================================================

for i in range(len(marker_df)-1):

    marker = marker_df.iloc[i]["marker"]

    start_t = marker_df.iloc[i]["timestamp"]

    end_t = marker_df.iloc[i+1]["timestamp"]

    # -------------------------------------------------
# DETERMINE LABEL
# -------------------------------------------------

    if "LEFT_SYMBOL_START" in marker:

        label = "LEFT_SYMBOL"

    elif "RIGHT_SYMBOL_START" in marker:

        label = "RIGHT_SYMBOL"

    elif "Foot_SYMBOL_START" in marker:

        label = "Foot_SYMBOL"

    elif "DOWN_SYMBOL_START" in marker:

        label = "DOWN_SYMBOL"

    elif "LEFT_START" in marker:

        label = "LEFT"

    elif "RIGHT_START" in marker:

        label = "RIGHT"

    elif "Foot_START" in marker:

        label = "Foot"

    elif "DOWN_START" in marker:

        label = "DOWN"

    elif "REST_START" in marker:

        label = "REST"

    elif "FIXATION_START" in marker:

        label = "FIXATION"

    elif "MEDITATION_START" in marker:

        label = "MEDITATION"

    else:

        continue

    # -------------------------------------------------
    # APPLY LABEL INSIDE TIMESTAMP WINDOW
    # -------------------------------------------------

    mask = (

        (eeg_df["timestamp"] >= start_t)

        &

        (eeg_df["timestamp"] < end_t)

    )

    eeg_df.loc[
        mask,
        "label"
    ] = label

# =====================================================
# INVALIDATE DISCONTINUITIES
# =====================================================

for idx in loss_indices:

    start = max(
        0,
        idx - INVALID_WINDOW
    )

    end = min(
        len(eeg_df)-1,
        idx + INVALID_WINDOW
    )

    eeg_df.loc[
        start:end,
        "label"
    ] = "INVALID"

    eeg_df.loc[
        start:end,
        "validity"
    ] = "PACKET_DISCONTINUITY"

# =====================================================
# FINAL SAVE
# =====================================================

output_file = "final_dataset.csv"

eeg_df.to_csv(
    output_file,
    index=False
)

# =====================================================
# FINAL STATS
# =====================================================

duration = (

    eeg_df["timestamp"].iloc[-1]

    -

    eeg_df["timestamp"].iloc[0]

)

print("\n===================================")

print("FINAL DATASET SAVED")

print("FILE:",
      output_file)

print("\nTOTAL ROWS:",
      len(eeg_df))

print("\nDURATION:",
      round(duration, 3),
      "sec")

print("\nESTIMATED HZ:",
      round(len(eeg_df)/duration, 2))

print("\nINVALID ROWS:",
      (eeg_df["label"] == "INVALID").sum())

print("\nNO_LABEL ROWS:",
      (eeg_df["label"] == "NO_LABEL").sum())

print("\nVALID TASK ROWS:",
      (
          (eeg_df["label"] != "INVALID")
          &
          (eeg_df["label"] != "NO_LABEL")
      ).sum())

print("\nLABEL DISTRIBUTION:\n")

print(
    eeg_df["label"].value_counts()
)

print("\n===================================\n")