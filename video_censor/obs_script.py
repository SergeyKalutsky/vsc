import obspython as obs
import os
import zmq


context = zmq.Context()
socket = context.socket(zmq.REP)
socket.RCVTIMEO = 0

def script_description():
    return "Blurs the recording if inappropriate imagery detected"


def blur(pred):
    #switches blur on if probability is high
    source = obs.obs_get_source_by_name('blur')
    state = obs.obs_source_enabled(source)
    if state and pred <= 0.45:
        obs.obs_source_set_enabled(source, False)
    if not state and pred > 0.45:
        obs.obs_source_set_enabled(source, True)
    obs.obs_source_release(source)


def update_status():
    try:
        msg = socket.recv()
        print (msg)
        socket.send(b"to clien")
    except zmq.Again:
        print('failed')

def script_unload():
    socket.setsockopt(zmq.LINGER, 0) 
    socket.close()
    context.term()


def script_update(settings):
    port = "5557"
    socket.bind("tcp://*:%s" % port)
    obs.timer_add(update_status, 1000)


    # path = obs.obs_data_get_string(settings, "path")
    # pred = get_pred()
    # if pred is not None:
    #     print("Script is running!")


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "path", "Full path to communicator.txt", obs.OBS_TEXT_DEFAULT)
    return props
