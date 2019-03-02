import obspython as obs

def blur():
    with open(r'C:\Users\immmaggo\Desktop\final_censor\communicator.txt', 'r') as f:
        try:
            pred = float(f.read())
        except:
            pass
    source = obs.obs_get_source_by_name('blurr')
    state = obs.obs_source_enabled(source)
    if state and pred < 0.4:
        obs.obs_source_set_enabled(source, False)
    if not state and pred > 0.4:
        obs.obs_source_set_enabled(source, True)
    obs.obs_source_release(source)

# called at startup
def script_load(settings):
    obs.timer_add(blur, 15)
