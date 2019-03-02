import obspython as obs
import os

def script_description():
    return "Blurs the recording if inappropriate imagery detected"


def blur():
    #switches blur on if probability is high
    pred = get_pred()
    source = obs.obs_get_source_by_name('blur')
    state = obs.obs_source_enabled(source)
    if state and pred <= 0.45:
        obs.obs_source_set_enabled(source, False)
    if not state and pred > 0.45:
        obs.obs_source_set_enabled(source, True)
    obs.obs_source_release(source)


def get_pred():
    global path

    try:
        with open(os.path.normcase(path), "r") as f:
            return float(f.read())
    except:
        pass


def script_update(settings):
    global path

    path = obs.obs_data_get_string(settings, "path")
    pred = get_pred()
    if pred is not None:
        print("Script is running")
        obs.timer_add(blur, 15)


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "path", "Full path to communicator.txt", obs.OBS_TEXT_DEFAULT)
    return props
