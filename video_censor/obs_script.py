import obspython as obs
import os
import zmq
import sys


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
        pred = float(socket.recv())
        socket.send(b"to clien")
        blur(pred)
    except zmq.Again:
        pass


def script_update(settings):
    port = "5557"
    socket.bind("tcp://*:%s" % port)
    obs.timer_add(update_status, 15)


def script_properties():
    props = obs.obs_properties_create()
    return props
