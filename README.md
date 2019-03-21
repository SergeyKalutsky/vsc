# videostream_censor
Real time video recording censor 


<a href="http://freegifmaker.me/images/2ewNE/"><img src="http://i.freegifmaker.me/1/5/5/1/5/1/15515155322964920.gif?1551515545" alt="gifs website"/> <a href="http://freegifmaker.me/images/2ewNK/"><img src="http://i.freegifmaker.me/1/5/5/1/5/1/15515157402964953.gif?1551515751" alt="gifs website"/></a>


Project combines obs script and mobilenets models for real time NSFW classifiction of the video stream.
In case of detection of inappropriate imagery script tells obs to blur recording.

Small demonstrations of how it works:

https://www.youtube.com/watch?v=mGjkkCDoM00

https://www.youtube.com/watch?v=5ktVHWu-jgc&t=57s

### Requirements:

- python 3.6+
- pyzmq
- mss
- numpy
- opencv-python
- prefetch-generator
- tensorflow

### Installation:

1. Download python 3.6+
2. Clone or download this repository
3. Install dependencies:

  `$ pip install -r /path/to/requirements.txt`
  
 4. Add python path to OBS and upload script.
 5. Create new display source, crop the exact region you want to monitor on the underlying source and apply blur to it
 
 There are two ways to apply blur:
  - Streameffects https://obsproject.com/forum/resources/stream-effects.578/
  - Resize filter https://www.youtube.com/watch?v=8PODw_nHUbQ
  
  You can use either way, it shouldn't really matter since the source will be disabled most of the time.
 
 ##### note: 
 `Before desktop screenshot is fed to classifier it is resized to 224x224 pxl ratio. Obviously a lot of features of
 the image are lost due to compression. In this case the smaller initial screen region the better will be quality of resized image
 and prediction accuracy.`
 
 6. Configure scripts settings:

![img](https://i.imgur.com/YbnOuvM.jpg)
 
 - Project folder 
 Folder with obs_script and classifier. Configuration file will be saved to this folder. The path will be configured automatically if you haven't move obs script anywhere. Otherways you shoud either change the path or move saved conf.json file into project directory.
 - Prediction threshold
 From that value depends how "sure" algorithm should be in order to classify something as NSFW. If the value is to low there will be a lot of noise and false positives, if too high it may not react to inapropriate imagery.
 - Monitor number
 Number of the monitor, as spesified in os settings.
 - Port
 Socket port
 - Quiry interval(ms)
 How often should obs script update "blur status", depends on speed of a classifier.
 - Blur Source
 Name of a display source used to blur recording
 
