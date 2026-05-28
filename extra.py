from psychopy import visual, core, sound ,event
from pylsl import (
    StreamInlet,
    resolve_stream,
    StreamInfo,
    StreamOutlet
)

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
# BEEP
# =====================================================

beep = sound.Sound(
    value=1000,
    secs=0.2
)

# =====================================================
# SETTINGS
# =====================================================

meditation_duration = session["meditation_duration"]

fixation_duration = session["fixation_duration"]

symbol_duration = session["symbol_duration"]

task_duration = session["task_duration"]

rest_duration = session["rest_duration"]

trials = session["trials"]

# =====================================================
# SYMBOL MAP
# =====================================================

symbol_map = {

    "LEFT": "←",
    "RIGHT": "→",
    "UP": "↑",
    "DOWN": "↓"

}

# =====================================================
# BUILD TIMELINE
# =====================================================

timeline = []

current_time = 0.0

# -----------------------------------------------------
# INITIAL MEDITATION ONLY ONCE
# -----------------------------------------------------

timeline.append({

    "label": "MEDITATION",
    "display": "RELAX",
    "start": current_time,
    "end": current_time + meditation_duration

})

current_time += meditation_duration

# =====================================================
# REPEATING TRIALS
# =====================================================

for trial in trials:

    # -------------------------------------------------
    # FIXATION
    # -------------------------------------------------

    timeline.append({

        "label": "FIXATION",
        "display": "+",
        "start": current_time,
        "end": current_time + fixation_duration

    })

    current_time += fixation_duration

    # -------------------------------------------------
    # SYMBOL / CUE
    # -------------------------------------------------

    timeline.append({

        "label": f"{trial}_SYMBOL",
        "display": symbol_map[trial],
        "start": current_time,
        "end": current_time + symbol_duration

    })

    current_time += symbol_duration

    # -------------------------------------------------
    # MOTOR IMAGERY TASK
    # -------------------------------------------------

    timeline.append({

        "label": trial,
        "display": symbol_map[trial],
        "start": current_time,
        "end": current_time + task_duration

    })

    current_time += task_duration

    # -------------------------------------------------
    # REST
    # -------------------------------------------------

    timeline.append({

        "label": "REST",
        "display": "REST",
        "start": current_time,
        "end": current_time + rest_duration

    })

    current_time += rest_duration

TOTAL_DURATION = current_time

print("TOTAL DURATION:", TOTAL_DURATION)

# =====================================================
# SESSION START
# =====================================================

text.text = "+"
text.draw()

win.callOnFlip(
    marker_outlet.push_sample,
    ["SESSION_START"]
)

win.flip()

experiment_clock = core.Clock()

experiment_clock.reset()

last_label = None

beep_played = False

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    t = experiment_clock.getTime()

    if t >= TOTAL_DURATION:

        break

    current_event = None

    # -------------------------------------------------
    # FIND CURRENT EVENT
    # -------------------------------------------------

    for event in timeline:

        if event["start"] <= t < event["end"]:

            current_event = event

            break

    current_label = current_event["label"]

    current_display = current_event["display"]

    # -------------------------------------------------
    # BEEP IN LAST 3 SEC OF MEDITATION
    # -------------------------------------------------

    if current_label == "MEDITATION":

        meditation_end = current_event["end"]

        if (
            t >= meditation_end - 3
            and
            not beep_played
        ):

            beep.play()

            beep_played = True

    else:

        beep_played = False

    # -------------------------------------------------
    # SEND MARKER ON CHANGE
    # -------------------------------------------------

    if current_label != last_label:

        win.callOnFlip(

            marker_outlet.push_sample,
            [f"{current_label}_START"]

        )

        print(f"{current_label}_START")

        last_label = current_label

    # -------------------------------------------------
    # DISPLAY
    # -------------------------------------------------

    text.text = current_display

    text.draw()

    win.flip()

# =====================================================
# SESSION END
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