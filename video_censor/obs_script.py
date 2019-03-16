import obspython as obs
import zmq
import json
import os



# class OBS_Socket():
#     def __init__(self, port):
#         self.port = port

#     def connect(self):
#         context = zmq.Context()
#         consumer = context.socket(zmq.PULL)
#         poller = zmq.Poller()
#         poller.register(consumer, zmq.POLLIN)



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
    p1 = obs.obs_properties_add_list(p, "sources", "Blur Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_id(source)
            if source_id == "monitor_capture":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p1, name, name)
    obs.source_list_release(sources)
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
    global layer_name
    global threshold
    # Switches blur on if probability is high
    source = obs.obs_get_source_by_name(layer_name)
    state = obs.obs_source_enabled(source)
    if state and pred <= threshold:
        obs.obs_source_set_enabled(source, False)
    if not state and pred > threshold:
        obs.obs_source_set_enabled(source, True)
    obs.obs_source_release(source)


def update_status():
    if poller.poll(0):
        msg = consumer.recv_pyobj()
        blur(msg)


def script_update(settings):
    global project_dir
    global conf
    global layer_name
    global threshold
    project_dir = obs.obs_data_get_string(settings, "project_dir")
    threshold = obs.obs_data_get_double(settings, "pred_threshold")
    interval = obs.obs_data_get_int(settings, "interval")
    port =  obs.obs_data_get_int(settings, "port")
    layer_name = obs.obs_data_get_string(settings, "sources")

    conf = {"monitor": obs.obs_data_get_int(settings, "monitor_num"),
            "port": port,
            }

    consumer.bind(f"tcp://127.0.0.1:{port}")
    obs.timer_add(update_status, interval)

