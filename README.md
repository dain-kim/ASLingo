# ASLingo

ASLingo is a visual and interactive language learning tool for American Sign Language. Learn the letters of the alphabet in ASL by following the guide video in the learning mode. Then, once you're ready, test yourself in the game mode by spelling out as many words as possible before the timer runs out.

## Table of Contents

- [How to Run](#how-to-run)
- [Data Collection and Processing](#data-collection-and-processing)
- [Recognition Model](#recognition-model)
- Webcam Handler
- App
- Learning Mode & Game Mode

## How to Run

Environment setup:

```
conda create -n aslingo python=3.8
conda activate aslingo
pip install -r requirements.txt
python check_install.py
```

Running the main app:

```
python app.py
```

Most levels are locked in the beginning. To override level locking and see all levels, run:

```
python app.py -godmode
```

## Data Collection and Processing

`data_collection.py` generates the ASL letters data for training the recognition model. It gets the videos from three sources and runs them through MediaPipe to get the hand and pose data. The intermediate Mediapipe objects are parsed into a pandas DataFrame and saved 





for training the recognition model. It gets the videos from three sources and runs them through MediaPipe to get the hand and pose information. The parsed data and the video metadata are then stored in two separate files.



generates the data folder by fetching the video url from the ASL signbank website, extracting the hand and pose data from the video using MediaPipe, and converting and saving the data into a csv file. It also saves the source video url and a list of synonyms for each word into a metadata file.

Mediapipe returns the data at each frame as a SolutionOutputs object, which needs to be further unpacked. 

Data source: [ASL SignBank](https://aslsignbank.haskins.yale.edu), https://www.youtube.com/watch?v=tkMg8g8vVUo 



[hand landmarks indices](https://google.github.io/mediapipe/images/mobile/hand_landmarks.png)

[upper body landmarks indices](https://google.github.io/mediapipe/images/mobile/pose_tracking_upper_body_landmarks.png)

## 

## Recognition Model





## Learning Mode



## Game Mode





## UI

https://github.com/PySimpleGUI/PySimpleGUI

`python main.py` is an old script that attempts to use PySimpleGUI. using kivy instead: `python app.py`





### Notes

SignBank copyrights https://aslsignbank.haskins.yale.edu/about/conditions/



#### References:

https://towardsdatascience.com/american-sign-language-hand-gesture-recognition-f1c4468fb177

https://github.com/harshbg/Sign-Language-Interpreter-using-Deep-Learning#general-info

https://github.com/chenson2018/APM-Project

