import obspython as obs
import zmq
import json
import os

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.RCVTIMEO = 0


def script_description():
    return "Blurs the recording if inappropriate imagery detected"


def script_properties():
    p = obs.obs_properties_create()
    obs.obs_properties_add_path(p, "project_dir", "Project folder",
                                obs.OBS_PATH_DIRECTORY, "", os.path.expanduser("~"))
    obs.obs_properties_add_float_slider(p, "pred_threshold", "Prediction Threshold", 0.0, 1.0, 0.05)
    obs.obs_properties_add_int(p, "monitor_num", "Monitor Number", 1, 100, 1)
    obs.obs_properties_add_int(p, "port", "Port", 1, 10000, 1)
    obs.obs_properties_add_int(p, "interval", "Quiery interval(ms)", 1, 1000, 1)
    obs.obs_properties_add_button(p, "saved", "Save Configurations", button_pressed)
    return p

def script_defaults(settings):
    obs.obs_data_set_default_double(settings, "pred_threshold", 0.5)
    obs.obs_data_set_default_int(settings, "monitor_num", 1)
    obs.obs_data_set_default_int(settings, "port", 5557)
    obs.obs_data_set_default_int(settings, "interval", 33)

def button_pressed(properties, button):
    global project_dir
    global conf
    conf["coordinates"] = get_coordinates()
    with open(os.path.join(project_dir, "conf.json"), "w") as f:
        json.dump(conf, f)
    print("Configurations has been saved")
    return True

def get_sceneitem():
    source = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(source)
    sceneitem = obs.obs_scene_find_source(scene, 'blur')
    obs.obs_source_release(source)
    return sceneitem


def get_scene_size():
    source = obs.obs_get_source_by_name('blur')
    w = obs.obs_source_get_width(source)
    h = obs.obs_source_get_height(source)
    obs.obs_source_release(source)
    return w, h


def sceneitem_croped_size(crop):
    w, h = get_scene_size()
    w -= crop.left + crop.right
    h -= crop.top + crop.bottom
    return w, h


def get_coordinates():

    sceneitem = get_sceneitem()
    
    # Starting position
    pos = obs.vec2()
    obs.obs_sceneitem_get_pos(sceneitem, pos)
    # Scale ratio
    ratio = obs.vec2()
    obs.obs_sceneitem_get_scale(sceneitem, ratio)
    # Crop values
    crop = obs.obs_sceneitem_crop()
    obs.obs_sceneitem_get_crop(sceneitem, crop)

    w, h = sceneitem_croped_size(crop)
    w *= ratio.x
    h *= ratio.y

    coordinates = {"top": int(pos.y), 
                   "left": int(pos.x), 
                   "width": int(w), 
                   "height": int(h)}

    return coordinates


def blur(pred):
    # Switches blur on if probability is high
    source = obs.obs_get_source_by_name('blur')
    state = obs.obs_source_enabled(source)
    if state and pred <= 0.45:
        obs.obs_source_set_enabled(source, False)
    if not state and pred > 0.45:
        obs.obs_source_set_enabled(source, True)
    obs.obs_source_release(source)


def update_status():
    try:
        msg = socket.recv_json()
        # Update screenshot area to selected region in OBS
        if msg["act"] == "get screen region":
            socket.send_json(get_coordinates())
        # Change visibility of "blur" layer based on prediction value
        elif msg["act"] == "stream censor":
            blur(msg['pred'])
            socket.send_json({})
    except zmq.Again:
        pass


def script_update(settings):
    global project_dir
    global conf
    project_dir = obs.obs_data_get_string(settings, "project_dir")
    threshold = obs.obs_data_get_double(settings, "pred_threshold")
    interval = obs.obs_data_get_int(settings, "interval")
    port =  obs.obs_data_get_int(settings, "port")

    conf = {"monitor": obs.obs_data_get_int(settings, "monitor_num"),
            "port": port,
            }
    """ socket.bind("tcp://*:5557")
             obs.timer_add(update_status, 8)"""

