import obspython as obs
# import os
# import zmq
# import sys




def script_update(settings):
    pos = obs.vec2()

    source = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(source)

    # w =
    obs.obs_source_release(source)

    sceneitem = obs.obs_scene_find_source(scene, 'blur')
    obs.obs_sceneitem_get_pos(sceneitem, pos)
    print(pos.x, pos.y)

    crop = obs.obs_sceneitem_crop()
    obs.obs_sceneitem_get_crop(sceneitem, crop)
    print(crop.left, crop.right)
    # obs.obs_source_release(source)
























# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.RCVTIMEO = 0


# def script_description():
#     return "Blurs the recording if inappropriate imagery detected"


# def blur(pred):
#     #switches blur on if probability is high
#     source = obs.obs_get_source_by_name('blur')
#     state = obs.obs_source_enabled(source)
#     if state and pred <= 0.45:
#         obs.obs_source_set_enabled(source, False)
#     if not state and pred > 0.45:
#         obs.obs_source_set_enabled(source, True)
#     obs.obs_source_release(source)


# def update_status():
#     try:
#         pred = float(socket.recv())
#         socket.send(b"to clien")
#         blur(pred)
#     except zmq.Again:
#         pass


# def script_update(settings):
#     #Create a server
#     socket.bind("tcp://*:5557")
#     obs.timer_add(update_status, 3)


# def script_properties():
#     props = obs.obs_properties_create()
#     return props
