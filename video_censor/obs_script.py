import obspython as obs
import zmq
import json
import os


class OBS_Socket():
    def __init__(self, socket_type=zmq.REP, poller_type=zmq.POLLIN):
        self._port = 0
        self.socket = zmq.Context().socket(socket_type)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, poller_type)

    def bind(self, port):

        if not self._port:
            self.socket.bind(f"tcp://127.0.0.1:{port}")
            self._port = port

        elif self._port != port:
            self.socket.unbind(f"tcp://127.0.0.1:{self._port}")
            self.socket.bind(f"tcp://127.0.0.1:{port}")
            self._port = port

    def poll(self, rcv_time=0):
        return self.poller.poll(rcv_time)
    
    def recv(self):
        return self.socket.recv_pyobj()

    def send(self, msg=b""):
        return self.socket.send(msg)


class OBS_ScriptSettings():

    getter_fun = {bool: obs.obs_data_get_bool, str: obs.obs_data_get_string,
                  int: obs.obs_data_get_int, float: obs.obs_data_get_double}
    default_fun = {bool: obs.obs_data_set_default_bool, str: obs.obs_data_set_default_string,
                   int: obs.obs_data_set_default_int, float: obs.obs_data_set_default_double}

    settings = {"project_dir": "",
                "pred_threshold": 0.5,
                "monitor_num": 1,
                "port": 5557,
                "interval": 30,
                "source": ""
    }

    def __init__(self):
        self.prop_obj = None

    def create_properies(self):
        self.prop_obj = obs.obs_properties_create()

    def add_path(self, name, description):
        obs.obs_properties_add_path(self.prop_obj, name, description,
                                    obs.OBS_PATH_DIRECTORY, "", os.path.expanduser("~"))

    def add_int(self, name, description, vals):
        obs.obs_properties_add_int(self.prop_obj, name, description, *vals)

    def add_float_slider(self, name, description, vals):
        obs.obs_properties_add_float_slider(self.prop_obj, name, description, *vals)

    def add_list(self, name, description, source_type):
        p = obs.obs_properties_add_list(self.prop_obj, name, description, 
                                        obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

        def _add_sources(source_type, prop):
            sources = obs.obs_enum_sources()
            if sources is not None:
                for source in sources:
                    source_id = obs.obs_source_get_id(source)
                    if source_id == source_type:
                        name = obs.obs_source_get_name(source)
                        obs.obs_property_list_add_string(prop, name, name)
            obs.source_list_release(sources)

        _add_sources(source_type, p)

    def add_button(self, name, description, callback):
        obs.obs_properties_add_button(self.prop_obj, name, description, callback)

    def set_defaults(self, settings):
        for name, value in self.settings.items():
            self.default_fun[type(value)](settings, name, value)

    def update(self, settings):
        for name, value in self.settings.items():
                self.settings[name] = self.getter_fun[type(value)](settings, name)


socket = OBS_Socket()
script = OBS_ScriptSettings()


def script_description():
    return "Blurs the recording if inappropriate imagery detected"


def script_properties():
    script.create_properies()
    script.add_path("project_dir", "Project folder")
    script.add_float_slider("pred_threshold", "Prediction Threshold", (0.0, 1.0, 0.05))
    script.add_int("monitor_num", "Monitor Number", (1, 100, 1))
    script.add_int("port", "Port", (1, 10000, 1))
    script.add_int("interval", "Quiery interval(ms)", (1, 10000, 1))
    script.add_list("source", "Blur Source", source_type="monitor_capture")
    script.add_button("save", "Save Configurations", button_pressed)
    return script.prop_obj

def button_pressed(properties, button):
    conf = script.settings.copy()
    conf['coordinates'] = get_coordinates()
    with open(os.path.join(conf["project_dir"], "conf.json"), "w") as f:
            json.dump(conf, f)
    print("Configurations has been saved")
    return True

def script_defaults(settings):
    script.set_defaults(settings)


def get_sceneitem_by_source(source_name):
    source = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(source)
    sceneitem = obs.obs_scene_find_source(scene, source_name)
    obs.obs_source_release(source)
    return sceneitem


def get_source_size(source_name):
    source = obs.obs_get_source_by_name(source_name)
    w = obs.obs_source_get_width(source)
    h = obs.obs_source_get_height(source)
    obs.obs_source_release(source)
    return w, h


def source_croped_size(source_size, crop):
    w, h = source_size
    w -= crop.left + crop.right
    h -= crop.top + crop.bottom
    return w, h


def get_coordinates():
    source_name = script.settings['source']
    sceneitem = get_sceneitem_by_source(source_name)
    
    # Starting position
    pos = obs.vec2()
    obs.obs_sceneitem_get_pos(sceneitem, pos)
    # Scale ratio
    ratio = obs.vec2()
    obs.obs_sceneitem_get_scale(sceneitem, ratio)
    # Crop values
    crop = obs.obs_sceneitem_crop()
    obs.obs_sceneitem_get_crop(sceneitem, crop)

    w, h = get_source_size(source_name)
    w, h = source_croped_size((w, h), crop)
    w *= ratio.x
    h *= ratio.y

    coordinates = {"top": int(pos.y), 
                   "left": int(pos.x), 
                   "width": int(w), 
                   "height": int(h)}

    return coordinates

def blur(set_blur):
    # Switches blur on if probability is high
    source = obs.obs_get_source_by_name(layer_name)
    blured = obs.obs_source_enabled(source)
    if blured and not set_blur:
        obs.obs_source_set_enabled(source, False)
    if not blured and set_blur:
        obs.obs_source_set_enabled(source, True)
    obs.obs_source_release(source)


def update_status():
    if socket.poll():
        msg = socket.recv()
        socket.send()
        blur(msg)


def script_update(settings):
    script.update(settings)
    socket.bind(script.settings['port'])
    obs.timer_add(update_status, script.settings['interval'])

