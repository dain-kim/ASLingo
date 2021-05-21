# ASLingo

ASLingo is a visual and interactive language learning tool for American Sign Language. Learn the letters of the alphabet in ASL by following the guide video in the learning mode. Then, once you're ready, test yourself in the game mode by spelling out as many words as possible before the timer runs out.

## Table of Contents

- [How to Run](#how-to-run)
- [Data Collection and Processing](#data-collection-and-processing)
- [Recognition Model](#recognition-model)
- [VideoHandler](#videohandler)
- [Learning Mode](#learning-mode)
- [Game Mode](#game-mode)
- [Credits](#credits)
- [Inspirations](#inspirations)

## How to Run

You should have [miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.

Environment setup:

```
cd ASLingo
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

`data_collection.py` generates the ASL letters data for training the recognition model. It gets the videos from three sources and runs them through MediaPipe to get the hand and pose data. The intermediate Mediapipe objects are parsed into a pandas DataFrame and saved in the `data/` folder for training the recognition model. The video metadata is also saved in a separate file, `data/metadata.json`, to be used later.

### Data csv format

The collected data is formatted into a csv file with the following information: the normalized xyz-coordinates of the [21 MediaPipe hand landmarks](https://google.github.io/mediapipe/images/mobile/hand_landmarks.png) for each hand, the normalized xyz-coordinates of the [25 MediaPipe upper body landmarks](https://google.github.io/mediapipe/images/mobile/pose_tracking_upper_body_landmarks.png), and the timestamp of the frame. 

| timestamp | lefthand_0_x | ...  | lefthand_20_z | righthand_0_x | ...  | righthand_20_z | pose_0_x | ...  | pose_24_z |
| --------- | ------------ | ---- | ------------- | ------------- | ---- | -------------- | -------- | ---- | --------- |
| 0.0       |              |      |               |               |      |                |          |      |           |

1 + 21 * 3 * 2 + 25 * 3 = **202** columns, **num_frames** rows

Data columns are named in the format "type_idx_coord", where:

- **type** is one of `lefthand`, `righthand`, `pose`
- **idx** is the joint index as defined in MediaPipe
- **coord** is one of `x`, `y`, `z`

### Metadata json format

This is a dictionary that contains info like synonyms and video sources for each word. This is the format:

```
{'HELLO': {
	'synonyms': ['hi','hey'], 
	'video_src': {'0': 'video/path/for/data/HELLO/0.csv'}
	},
'BYE': {
 	'synonyms': ['goodbye'],
 	'video_src': {'0': 'video/path/for/data/BYE/0.csv',
 								'1': 'video/path/for/data/BYE/1.csv'}
	}
}
```

## Recognition Model

`train_model.ipynb` contains the code used for training the recognition model. The LSTM, CNN, LDA, QDA, KNN, Random Forest, and GaussianNB architectures were tested to find the ideal framework for this project that is both fast and accurate. The LinearDiscriminantAnalysis classifier was chosen for the final model. Helper functions can be found in the notebook for plotting and comparing the model performance, visualizing the hand data, and generating more data from one video source by selectively perturbing the original data.

## VideoHandler

The VideoHandler class connects the trained model and the video input. It continually receives data from the live webcam feed and generates a data buffer of fixed length at each frame. The model is applied to the buffer to produce a prediction: one of the 26 letters, “Neutral”, or “No hands detected”. The class also contains a helper function for evaluating the model’s performance on unseen video data. It uses pre-recorded videos in *test_webcam_data/* to test each letter and print out the accuracy results.

## Learning Mode

In the learning mode, a guide video is shown for each of the letters in the set for the user to follow. When the user successfully follows the video (i.e. the gesture is correctly recognized), they move onto the next letter. Completing the entire set unlocks the review level. The review level shows no guide videos and expects the user to recall the letters on their own. If the user is stumped, they can use the keyboard to show the guide video. The user must be able to correctly remember all the letters in the set on their own, including the ones they watched the video for, before moving on to the next level. The shuffle level is nearly identical to the review level, but scrambles the order of the letters to provide an extra round of repetition.

## Game Mode

The game level is unlocked when the user finishes all three learning levels of the corresponding set. Here, the user is tested on their knowledge of the letters by spelling out the prompted words as quickly as possible. The easy level is 30 seconds long and contains short, 3-letter words. There is a 3-second countdown period in the beginning, and a timer bar at the bottom displays the remaining time during the game. At the end of the game, the user receives a score out of three stars based on how many words they’ve spelled correctly. The user must get at least one star to pass the level and move onto the next one. The harder levels contain slightly longer words and give more time for each round. The target words are randomly drawn from the level's word bank, which covers all the letters at least once. The word bank is cumulative: the first set of games contains words with the letters A through G, the next set covers A-N, and so on.

## Credits

### Video Sources

- [SigningSavvy](https://www.signingsavvy.com/), an online ASL video dictionary
- [SignBSL.com](https://www.signbsl.com/), an online British Sign Language video dictionary (The letters are spelled the same in both ASL and BSL)
- A [public youtube video](https://www.youtube.com/watch?v=tkMg8g8vVUo) by *ASL That*

### Code

- The `common/` directory contains parts of Kivy utilities code written by Eran Egozy (egozy@mit.edu), the professor for [the class I'm currently TA'ing](https://musictech.mit.edu/ims) that extensively uses Kivy. I received explicit permission from him beforehand, and the code is released under the MIT License.

### Libraries

- [MediaPipe](https://google.github.io/mediapipe/getting_started/python)==0.8.3.1
- [Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html)==2.0.0
- [OpenCV](https://pypi.org/project/opencv-python/)

To train the model:

- jupyter
- scikit-learn
- keras
- tensorflow

To make nice graphs:

- matplotlib

## Inspirations:

https://towardsdatascience.com/american-sign-language-hand-gesture-recognition-f1c4468fb177

https://github.com/harshbg/Sign-Language-Interpreter-using-Deep-Learning#general-info

https://github.com/chenson2018/APM-Project

