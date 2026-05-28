from pylsl import StreamInfo, StreamOutlet
import json
import random
import time

# =====================================================
# PHASE DURATIONS
# =====================================================

MEDITATION_DURATION = 10
FIXATION_DURATION = 3
SYMBOL_DURATION = 2
TASK_DURATION = 5
REST_DURATION = 5

# =====================================================
# CLASSES
# =====================================================

classes = [
    "LEFT",
    "RIGHT",
    "Foot",
    "DOWN"
]

# 3 trials -> 60 sec total
trial_sequence = [
    "LEFT",
    "RIGHT",
    "Foot",
    "DOWN"
]

random.shuffle(trial_sequence)

# =====================================================
# TOTAL DURATION
# =====================================================

SINGLE_TRIAL_DURATION = (

    MEDITATION_DURATION
    + FIXATION_DURATION
    + SYMBOL_DURATION
    + TASK_DURATION
    + REST_DURATION

)

TOTAL_DURATION = (
    SINGLE_TRIAL_DURATION
    * len(trial_sequence)
)

# =====================================================
# CREATE CONTROL STREAM
# =====================================================

info = StreamInfo(

    name='control',
    type='Control',
    channel_count=1,
    nominal_srate=0,
    channel_format='string',
    source_id='control_stream_001'

)

outlet = StreamOutlet(info)

# =====================================================
# SESSION CONFIG
# =====================================================

session = {

    "command": "START",

    "meditation_duration": MEDITATION_DURATION,

    "fixation_duration": FIXATION_DURATION,

    "symbol_duration": SYMBOL_DURATION,

    "task_duration": TASK_DURATION,

    "rest_duration": REST_DURATION,

    "trials": trial_sequence,

    "total_duration": TOTAL_DURATION

}

# =====================================================
# START
# =====================================================

input("\nPress ENTER to START experiment...\n")

outlet.push_sample([json.dumps(session)])

print("\nSTART SENT\n")

print("Trials:")
print(trial_sequence)

print("\nTOTAL DURATION:",
      TOTAL_DURATION)

# =====================================================
# KEEP STREAM ALIVE
# =====================================================

time.sleep(TOTAL_DURATION + 5)

print("\nController finished\n")