# videostream_censor
Real time video recording censor 

<a href="http://freegifmaker.me/images/2ewNE/"><img src="http://i.freegifmaker.me/1/5/5/1/5/1/15515155322964920.gif?1551515545" alt="gifs website"/> <a href="http://freegifmaker.me/images/2ewNK/"><img src="http://i.freegifmaker.me/1/5/5/1/5/1/15515157402964953.gif?1551515751" alt="gifs website"/></a>


Project combines obs script and mobilenets models for real time NSFW classifiction of the video stream.
In case of detection of inappropriate imagery script tells obs to blur recording.

Small demonstrations of how it works:

https://www.youtube.com/watch?v=mGjkkCDoM00

https://www.youtube.com/watch?v=5ktVHWu-jgc&t=57s

## Requirements

- python 3.6+
- pyzmq
- mss
- numpy
- opencv-python
- prefetch-generator
- tensorflow

## Installation

1. Download python 3.6+
2. Clone or download this repository
3. Install dependencies:
<div class="highlight highlight-source-shell">
  <pre>$ pip install -r /path/to/requirements.txt</pre>
 </div>
  
 4. Add python path to OBS and upload script.
 5. Create new display source, crop the exact region you want to monitor on the underlying source and apply blur to it
 
#### There are two ways to apply blur:
  - Streameffects https://obsproject.com/forum/resources/stream-effects.578/
  - Resize filter https://www.youtube.com/watch?v=8PODw_nHUbQ
  
  You can use either way, it shouldn't really matter since the source will be disabled most of the time.
 
 #### Important note: 
 `Before desktop screenshot is fed to classifier it is resized to 224x224 pxl ratio. Obviously a lot of features of
 the image are lost due to compression. In this case the smaller initial screen region the better will be quality of resized image
 and prediction accuracy.`
 
 6. Configure scripts settings:

![img](https://i.imgur.com/YbnOuvM.jpg)
<table>
  <thead valign="bottom">
    <tr>
      <th>
        Setting
      </th>
      <th>
        Description
      </th>
    </tr>
  </thead>
<tr> 
  <td>Project folder</td>
  <td>Folder with obs_script and classifier. Configuration file will be saved to this folder. the path will be configured automatically if you haven't move obs script anywhere. otherways you shoud either change the path or move saved conf.json file into project directory.    </td>
</tr>
<tr> 
  <td>Prediction threshold</td>
  <td>From that value depends how "sure" algorithm should be in order to classify something as NSFW. If the value is to low there will be a lot of noise and false positives, if too high it may not react to inapropriate imagery.    </td>
</tr>
<tr> 
  <td>Monitor number</td>
  <td>Number of the monitor, as spesified in os settings.</td>
</tr>
<tr> 
  <td>Port</td>
  <td> Socket port</td>
</tr>
<tr> 
  <td>Quiry interval(ms)</td>
  <td>How often should obs script update "blur status", depends on speed of a classifier.</td>
</tr>
<tr> 
  <td>Blur Source</td>
  <td>Name of a display source used to blur recording.</td>
</tr>
</table>
 
 7. Save configurations and disable source
 8. run classifier.py
 <div class="highlight highlight-source-shell">
  <pre>$ python path/to/classifier.py -v</pre>
 </div>
 
