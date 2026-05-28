from psychopy import visual, core, sound, event
from psychopy.hardware import keyboard
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

    size=[1920, 1080],
    fullscr=True,
    color='black',
    allowGUI=False,
    units='height'

)

# Reliable keyboard object
kb = keyboard.Keyboard()

event.clearEvents()
kb.clearEvents()

# =====================================================
# ABORT FUNCTION
# =====================================================

def abort_session():

    print("\nSESSION_ABORT\n")

    try:
        marker_outlet.push_sample(["SESSION_ABORT"])
        core.wait(0.2)

    except Exception as e:
        print("Could not send SESSION_ABORT marker:", e)

    try:
        win.close()

    except Exception:
        pass

    core.quit()

# =====================================================
# TEXT STIMULUS
# =====================================================

text = visual.TextStim(

    win,
    text="",
    color='white',
    height=0.15,
    font='Arial'

)

# =====================================================
# IMAGE STIMULUS
# =====================================================

cue_image = visual.ImageStim(

    win,
    image=None,
    size=(0.35, 0.35)

)

# =====================================================
# BEEP
# =====================================================

beep = sound.Sound(
    value=1000,
    secs=0.2
)

# 3 beeps in last 3 seconds of meditation
BEEP_TIMES_BEFORE_END = [3, 2, 1]
played_beeps = set()

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
# IMAGE MAP
# =====================================================

symbol_map = {

    "LEFT": "emoji_cues/left.png",
    "RIGHT": "emoji_cues/right.png",
    "Foot": "emoji_cues/foot.png",
    "DOWN": "emoji_cues/down.png"

}

# =====================================================
# BUILD TIMELINE
# =====================================================

timeline = []

current_time = 0.0

# -----------------------------------------------------
# INITIAL MEDITATION
# -----------------------------------------------------

timeline.append({

    "label": "MEDITATION",
    "display_type": "text",
    "display": "RELAX",
    "start": current_time,
    "end": current_time + meditation_duration

})

current_time += meditation_duration

# =====================================================
# MAIN TRIALS
# =====================================================

for trial in trials:

    # -------------------------------------------------
    # FIXATION
    # -------------------------------------------------

    timeline.append({

        "label": "FIXATION",
        "display_type": "text",
        "display": "+",
        "start": current_time,
        "end": current_time + fixation_duration

    })

    current_time += fixation_duration

    # -------------------------------------------------
    # SYMBOL / IMAGE CUE
    # -------------------------------------------------

    timeline.append({

        "label": f"{trial}_SYMBOL",
        "display_type": "image",
        "display": symbol_map[trial],
        "start": current_time,
        "end": current_time + symbol_duration

    })

    current_time += symbol_duration

    # -------------------------------------------------
    # TASK
    # -------------------------------------------------

    timeline.append({

        "label": trial,
        "display_type": "image",
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
        "display_type": "text",
        "display": "REST",
        "start": current_time,
        "end": current_time + rest_duration

    })

    current_time += rest_duration

TOTAL_DURATION = current_time

print("TOTAL DURATION:", TOTAL_DURATION)

# =====================================================
# START CLOCK
# =====================================================

experiment_clock = core.Clock()
experiment_clock.reset()

last_label = None
session_started = False

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    # -------------------------------------------------
    # ESCAPE / Q KEY TO ABORT
    # -------------------------------------------------

    keys_event = event.getKeys(
        keyList=["escape", "q"]
    )

    keys_keyboard = kb.getKeys(
        ["escape", "q"],
        waitRelease=False
    )

    if keys_event or keys_keyboard:

        abort_session()

    # -------------------------------------------------
    # TIME
    # -------------------------------------------------

    t = experiment_clock.getTime()

    if t >= TOTAL_DURATION:

        break

    current_event = None

    # -------------------------------------------------
    # FIND CURRENT EVENT
    # -------------------------------------------------

    for ev in timeline:

        if ev["start"] <= t < ev["end"]:

            current_event = ev

            break

    if current_event is None:

        continue

    current_label = current_event["label"]

    current_display = current_event["display"]

    current_display_type = current_event["display_type"]

    # -------------------------------------------------
    # 3 BEEPS DURING LAST 3 SECONDS OF MEDITATION
    # -------------------------------------------------

    if current_label == "MEDITATION":

        meditation_end = current_event["end"]

        remaining = meditation_end - t

        for beep_time in BEEP_TIMES_BEFORE_END:

            if remaining <= beep_time and beep_time not in played_beeps:

                beep.play()

                played_beeps.add(beep_time)

    # -------------------------------------------------
    # SEND MARKER ON VISUAL FLIP
    # -------------------------------------------------

    if current_label != last_label:

        if not session_started:

            win.callOnFlip(
                marker_outlet.push_sample,
                ["SESSION_START"]
            )

            print("SESSION_START")

            session_started = True

        win.callOnFlip(

            marker_outlet.push_sample,
            [f"{current_label}_START"]

        )

        print(f"{current_label}_START")

        last_label = current_label

    # -------------------------------------------------
    # DISPLAY
    # -------------------------------------------------

    if current_display_type == "image":

        cue_image.image = current_display

        cue_image.draw()

    else:

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