from pylsl import StreamInfo, StreamOutlet
import json
import random
import time

# =====================================================
# SETTINGS
# =====================================================

TASK_DURATION = 3
REST_DURATION = 2

classes = [
    "LEFT",
    "RIGHT",
    "UP",
    "DOWN"
]

trial_sequence = classes * 3

random.shuffle(trial_sequence)

TOTAL_DURATION = (
    TASK_DURATION + REST_DURATION
) * len(trial_sequence)

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