# ASL Translator

Term project for 6.835 Intelligent Multimodal Interaction.

[hand landmarks indices](https://google.github.io/mediapipe/images/mobile/hand_landmarks.png)

[upper body landmarks indices](https://google.github.io/mediapipe/images/mobile/pose_tracking_upper_body_landmarks.png)

## Table of Contents

- [Data Collection](#data-collection)





## Data Collection

Data source: [ASL SignBank](https://aslsignbank.haskins.yale.edu), https://www.youtube.com/watch?v=tkMg8g8vVUo 

`data_collection.py` generates the data folder by fetching the video url from the ASL signbank website, extracting the hand and pose data from the video using MediaPipe, and converting and saving the data into a csv file. It also saves the source video url and a list of synonyms for each word into a metadata file. The script takes about 2 hours to run.

Mediapipe returns the data at each frame as a SolutionOutputs object, which needs to be further unpacked. 



## Game Mode





## UI

https://github.com/PySimpleGUI/PySimpleGUI

`python main.py` is an old script that attempts to use PySimpleGUI. using kivy instead: `python app.py`





### Notes

SignBank copyrights https://aslsignbank.haskins.yale.edu/about/conditions/

