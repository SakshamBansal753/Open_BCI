import pandas as pd

# =====================================================
# SETTINGS
# =====================================================

EXPECTED_HZ = 250

EXPECTED_DT = 1 / EXPECTED_HZ

LOSS_THRESHOLD = EXPECTED_DT * 4

ROLLING_WINDOW = 5

INVALID_WINDOW = 10

# =====================================================
# LOAD FILES
# =====================================================

print("\nLoading files...\n")

eeg_df = pd.read_csv("raw_eeg.csv")

marker_df = pd.read_csv("markers.csv")

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
# ROLLING CONTINUITY VALIDATION
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
# DETECT SUSTAINED DISCONTINUITIES
# =====================================================

eeg_df["packet_loss"] = (

    eeg_df["rolling_dt"] > LOSS_THRESHOLD

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

    # DETERMINE LABEL

    if "LEFT_START" in marker:

        label = "LEFT"

    elif "RIGHT_START" in marker:

        label = "RIGHT"

    elif "UP_START" in marker:

        label = "UP"

    elif "DOWN_START" in marker:

        label = "DOWN"

    elif "REST_START" in marker:

        label = "REST"

    else:

        continue

    # APPLY LABEL INSIDE INTERVAL

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
# INVALIDATE TRUE DISCONTINUITIES
# =====================================================

for idx in loss_indices:

    start = max(0, idx - INVALID_WINDOW)

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
# SAVE FINAL DATASET
# =====================================================

output_file = "final_motor_imagery_dataset.csv"

eeg_df.to_csv(
    output_file,
    index=False
)

# =====================================================
# FINAL STATS
# =====================================================

print("\n===================================")

print("FINAL DATASET SAVED")

print("FILE:", output_file)

print("\nTOTAL ROWS:",
      len(eeg_df))

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