import os, sys
import cv2
import numpy as np
import pandas as pd
import string
import mediapipe as mp
import pickle
from zipfile import ZipFile
from utils import StaticSignProcessor, mp_process_image, generate_dataframe, annotate_image, pred_class_to_letter


# load the model
with open('saved_model.pkl', 'rb') as f:
    model = pickle.load(f)

# TODO change to generic video src handler
class VideoHandler():
    def __init__(self, vid_src=0):
        self.cap = cv2.VideoCapture(vid_src)
        self.processor = StaticSignProcessor((126,))
        self.timestamps = []
        self.hand_results = []
        self.pose_results = []
        self.framecount = 0
        self.prediction = 'Neutral'
        self.score = ''
        self.pred_thresh = 0.7
        # self.colormap = {'No hands detected': (0,0,255), 'Neutral': (255,0,0)}
    
    def load_source(self, vid_src):
        self.cap.release()
        self.cap = cv2.VideoCapture(vid_src)

    def generate_buffer(self, frame, buffer_size=10, sliding_window=1, callback=None):
        '''
        Generates a buffer of fixed length from a live video stream
        to be processed and passed into the recognition model.
        
        Returns:
        A dict containing timestamps, hand_results, and pose_results
        if the buffer condition is met
        '''
        assert buffer_size > 0, 'Buffer size must be a positive number'
        assert sliding_window > 0, 'Sliding window size must be a positive number'
        assert buffer_size > sliding_window, 'Sliding window must be smaller than buffer'
        
        hand_result, pose_result = mp_process_image(frame)
        if not hand_result.multi_handedness:
            self.timestamps = []
            self.hand_results = []
            self.pose_results = []
            self.framecount = 0
            return

        # time is a construct
        self.timestamps.append(0.0)
        self.hand_results.append(hand_result)
        self.pose_results.append(pose_result)
        self.framecount += 1

        if (self.framecount % buffer_size == 0) or \
            (self.framecount % sliding_window == 0 and self.framecount > buffer_size):
            buf = {'timestamps': self.timestamps,
                   'hand_results': self.hand_results,
                   'pose_results': self.pose_results}
            self.timestamps = self.timestamps[sliding_window:]
            self.hand_results = self.hand_results[sliding_window:]
            self.pose_results = self.pose_results[sliding_window:]
            if callback:
                callback(buf)
            return buf
    
    def get_next_frame(self):
        '''
        Reads the next frame from the webcam and makes a prediction when applicable.
        Returns:
        - None if webcam feed is closed or can't read feed
        - annotated image if feed is open
        - annotated image, prediction, score if feed is open and buffer condition is met
        '''
        if not self.cap.isOpened():
            return
        success, image = self.cap.read()
        if not success:
            return
        
        buf = self.generate_buffer(image, buffer_size=10, sliding_window=1, callback=self.predict)
        
        # if blur:
        #     image = cv2.blur(image, (25,25))
        if self.hand_results:
            image = annotate_image(image, self.hand_results[-1], self.pose_results[-1])
        else:
            self.prediction = 'No hands detected'
            self.score = ''
        image = cv2.flip(image, 1)
        if self.prediction:
            if self.prediction == 'No hands detected':
                color = (0,0,255)
            elif self.prediction == 'Neutral':
                color = (255,0,0)
            else:
                color = (0,150,0)
            cv2.putText(image, self.prediction + '  ' + self.score, (50,80), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)

        return image, self.prediction, self.score

    def predict(self, buf):
        # Make a prediction on the generated buffer
        df = generate_dataframe(buf)
        data = self.processor.process(df)
        pred_prob = model.predict_proba([data])[0]
        pred_class = list(pred_prob).index(max(pred_prob))
        if max(pred_prob) < self.pred_thresh:
            self.prediction = 'Neutral'
            self.score = ''
        else:
            self.prediction = pred_class_to_letter(pred_class)[0]
            self.score = str(round(max(pred_prob),2))
    
    def get_frame(self):
        if self.cap.isOpened():
            success, frame = self.cap.read()
            return frame
    
    def stream_webcam(self):
        '''
        A helper function to demonstrate the VideoHandler's functionality.
        Note that this is a blocking function: it will keep running until the webcam feed is closed.
        '''
        while self.cap.isOpened():
            image,_,_ = self.get_next_frame()
            cv2.imshow('webcam', image)
            if cv2.waitKey(5) & 0xFF == 27:
                print('esc')
                break
        # out = self.get_next_frame()
        # while out:
        #     image,_,_ = out
        #     cv2.imshow('webcam', image)
        #     out = self.get_next_frame()
        #     if cv2.waitKey(5) & 0xFF == 27:
        #         print('esc')
        #         break
    
    def evaluate_model(self, show=False):
        '''
        A helper function for evaluating the recognition model's performance.
        It uses pre-recorded videos in test_webcam_data to test each letter.
        The videos in the test data were not used to train the model.
        '''
        if not os.path.isdir('test_webcam_data'):
            print('Unzipping test data...')
            with ZipFile('test_webcam_data.zip','r') as zipobj:
                zipobj.extractall()

        accuracy = 0
        for i in string.ascii_uppercase:
            print('input:', i)
            tmp = []
            vid_src = f"test_webcam_data/{i}.mp4"
            self.cap = cv2.VideoCapture(vid_src)
            while self.cap.isOpened():
                try:
                    image, pred, score = self.get_next_frame()
                    if pred not in ('Neutral','No hands detected'):
                        tmp.append(pred.replace('LETTER-',''))
                    if show:
                        cv2.imshow('webcam', image)
                        if cv2.waitKey(5) & 0xFF == 27:
                            print('esc')
                            break
                except:
                    break
            final_pred = max(set(tmp), key = tmp.count)
            print('prediction:', final_pred)
            if i == final_pred:
                print('CORRECT')
                accuracy += 1
            else:
                print('INCORRECT')
        
        print('\n\nFinal Accuracy: {}/26 ({}%)'.format(str(accuracy), round(accuracy/26, 2)))


if __name__ == "__main__":
    webcam = VideoHandler()
    # webcam.stream_webcam()
    webcam.evaluate_model(show=(len(sys.argv) > 1 and sys.argv[1] == '--show'))
