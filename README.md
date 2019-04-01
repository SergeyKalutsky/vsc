# videostream_censor
Real-time video stream censor. The project combines OBS script and mobilenet model for real-time NSFW classification of the video stream captured from display source. In case of inappropriate imagery detection, the script tells OBS to blur recording.


<a href="http://freegifmaker.me/images/2ewNE/">
  <img src="http://i.freegifmaker.me/1/5/5/1/5/1/15515155322964920.gif?1551515545" alt="gifs website"/> 
</a>
<a href="http://freegifmaker.me/images/2ewNK/">
   <img src="http://i.freegifmaker.me/1/5/5/1/5/1/15515157402964953.gif?1551515751" alt="gifs website"/>
</a>

Small demonstration of how it works. (Recording looks a little bit weird because it was done on gcloud VM):

https://www.youtube.com/watch?v=mGjkkCDoM00

https://www.youtube.com/watch?v=5ktVHWu-jgc&t=57s

## Requirements
### To run:
- Tensorflow
- Python 3.6+
- OBS Studio

### To run fast:
- OBS Studio
- Python 3.6+
- GPU version of Tensorflow
- NVIDIA® GPU card with CUDA® Compute Capability 3.5 or higher. See the list of CUDA-enabled [GPU cards](https://developer.nvidia.com/cuda-gpus)

## Installation

1. Download python 3.6+
2. Install Tensorflow
3. Clone or download this repository
4. Install dependencies:
<div class="highlight highlight-source-shell">
  <pre>$ pip install -r /path/to/requirements.txt</pre>
 </div>
  
 5. Add python path to OBS and upload script.
 6. Create new display source, crop the exact region you want to monitor on the underlying source and apply blur to it
 
#### There are two ways to apply blur:
  - Streameffects https://obsproject.com/forum/resources/stream-effects.578/
  - Resize filter https://www.youtube.com/watch?v=8PODw_nHUbQ
  
  You can do either way, it shouldn't really matter since the source will be disabled most of the time.
 
 #### Important note: 
Before desktop screenshot is fed to classifier it is resized to 224x224 pxl ratio. Obviously, a lot of features of the image are lost due to compression. In this case, the smaller initial screen region the better will be quality of the resized image and prediction accuracy.
 
 6. Configure scripts settings:

![img](https://imgur.com/ofxN0HW.jpg)
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
  <td>Prediction threshold</td>
  <td>How "sure" algorithm should be in order to classify something as NSFW.  If the value is to low there will be a lot of noise and false positives, if too high it may not detect problematic recording.</td>
</tr>
<tr> 
  <td>Monitor number</td>
  <td>Number of the display source monitor, as spesified in os settings.</td>
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
  <td>Name of thr display source used to blur recording.</td>
</tr>
</table>
 
 7. Disable source
 8. Run classifier.py
 <div class="highlight highlight-source-shell">
  <pre>$ python path/to/classifier.py -v --port=5557</pre>
 </div>
 
