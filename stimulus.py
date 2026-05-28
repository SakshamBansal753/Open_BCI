from psychopy import visual, core
from pylsl import (
    StreamInlet,
    resolve_stream,
    StreamInfo,
    StreamOutlet
)
from psychopy import event

import json

# =====================================================
# CONNECT CONTROL STREAM
# =====================================================

print("\nWaiting for control stream...\n")

control_stream = resolve_stream(
    'name',
    'control'
)[0]

control_inlet = StreamInlet(control_stream)

session = None

while session is None:

    sample, _ = control_inlet.pull_sample(
        timeout=1.0
    )

    if sample:

        session = json.loads(sample[0])

print("\nExperiment Started\n")

# =====================================================
# MARKER STREAM
# =====================================================

marker_info = StreamInfo(

    name='markers',
    type='Markers',
    channel_count=1,
    nominal_srate=0,
    channel_format='string',
    source_id='marker_stream_001'

)

marker_outlet = StreamOutlet(marker_info)

# =====================================================
# WINDOW
# =====================================================

win = visual.Window(

    size=[1920,1080],
    fullscr=True,
    color='black',
    allowGUI=False,
    units='height'

)

text = visual.TextStim(

    win,
    color='white',
    height=0.15

)

# =====================================================
# SETTINGS
# =====================================================

task_duration = session["task_duration"]

rest_duration = session["rest_duration"]

trials = session["trials"]

# =====================================================
# BUILD TIMELINE
# =====================================================

timeline = []

current_time = 0.0

for trial in trials:

    # REST

    timeline.append({

        "label": "REST",
        "start": current_time,
        "end": current_time + rest_duration

    })

    current_time += rest_duration

    # TASK

    timeline.append({

        "label": trial,
        "start": current_time,
        "end": current_time + task_duration

    })

    current_time += task_duration

TOTAL_DURATION = current_time

print("TOTAL DURATION:", TOTAL_DURATION)

# =====================================================
# SESSION START
# =====================================================

marker_outlet.push_sample(["SESSION_START"])

experiment_clock = core.Clock()

last_label = None

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    t = experiment_clock.getTime()

    if t >= TOTAL_DURATION:

        break

    current_label = "NO_LABEL"

    # FIND ACTIVE INTERVAL

    for event in timeline:

        if event["start"] <= t < event["end"]:

            current_label = event["label"]

            break

    # SEND MARKER ON CHANGE

    if current_label != last_label:

        if current_label != "NO_LABEL":
            win.callOnFlip(
                marker_outlet.push_sample,
                [f"{current_label}_START"]
            )

            print(f"{current_label}_START")
        last_label = current_label

    # DISPLAY

    text.text = current_label

    text.draw()

    win.flip()

# =====================================================
# SESSION END
# =====================================================
# =====================================================
# DONE SCREEN + SESSION END
# =====================================================

text.text = "DONE"

text.draw()

win.callOnFlip(
    marker_outlet.push_sample,
    ["SESSION_END"]
)

print("SESSION_END")

win.flip()

core.wait(2)

win.close()

core.quit()
