import os, sys
import cv2
import numpy as np
import pandas as pd
import string
import mediapipe as mp
import pickle
from zipfile import ZipFile
from utils import mp_process_image, generate_dataframe, annotate_image, pred_class_to_letter


# load the model
with open('saved_model.pkl', 'rb') as f:
    model = pickle.load(f)


class WebcamHandler():
    def __init__(self, vid_src=0):
        self.cap = cv2.VideoCapture(vid_src)
        self.image = None
        self.processor = StaticSignProcessor((126,))
        self.timestamps = []
        self.hand_results = []
        self.pose_results = []
        self.framecount = 0

    def generate_buffer(self, frame, buffer_size=10, sliding_window=1):
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

        # self.timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
        # time is a construct
        self.timestamps.append(0.0)
        self.hand_results.append(hand_result)
        self.pose_results.append(pose_result)
        self.framecount += 1

        if (self.framecount % buffer_size == 0) or (self.framecount % sliding_window == 0 and self.framecount > buffer_size):
            buf = {'timestamps': self.timestamps,
                   'hand_results': self.hand_results,
                   'pose_results': self.pose_results}
            self.timestamps = self.timestamps[sliding_window:]
            self.hand_results = self.hand_results[sliding_window:]
            self.pose_results = self.pose_results[sliding_window:]
            return buf
    
    def get_next_frame(self, pred_thresh=0.3):
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
        
        score = ''
        prediction = ''
        buf = self.generate_buffer(image, buffer_size=10, sliding_window=1)
        if buf:
            # Make a prediction on the generated buffer
            df = generate_dataframe(buf)
            data = self.processor.process(df)
            pred_prob = model.predict_proba([data])[0]
            pred_class = list(pred_prob).index(max(pred_prob))
            if max(pred_prob) < pred_thresh:
                # print('PREDICTED: NEUTRAL', max(pred_prob))
                pass
            else:
                prediction = pred_class_to_letter(pred_class)[0]
                score = str(round(max(pred_prob),2))
                # print('PREDICTED:', prediction, score)

        # if blur:
        #     image = cv2.blur(image, (25,25))
        if self.hand_results:
            image = annotate_image(image, self.hand_results[-1], self.pose_results[-1])
        else:
            prediction = 'No hands detected'
        image = cv2.flip(image, 1)
        if prediction:
            cv2.putText(image, prediction + '  ' + score, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

        return image, prediction, score
    
    def stream_webcam(self):
        '''
        A helper function to demonstrate the WebcamHandler's functionality.
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
                    if pred not in ('','No hands detected'):
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
            

# TODO move this to a separate script
class StaticSignProcessor():
    def __init__(self, X_shape=(10,126,1)):
        self.shape = X_shape
    
    def process(self, df):
        '''
        Processes the parsed data (DataFrame containing MediaPipe data objects)
        just the cleanup: cut out head and tail, fill nan, (normalize)
        '''
#         # Drop the frames in the beginning and end of the video where no hands are detected
#         start_idx = (~df['lefthand_0_x'].isna() | ~df['righthand_0_x'].isna()).argmax()
#         end_idx = len(df) - (df[::-1]['lefthand_0_x'].isna() & df[::-1]['righthand_0_x'].isna()).argmin()
# #         df = df.iloc[start_idx:end_idx]
#         # for lda
# #         df = df.iloc[start_idx:end_idx,1:]

#         # Fill empty values with the previous seen value
#         df = df.fillna(method='ffill')
#         df = df.fillna(method='bfill')
#         df = df.fillna(0.)
        
#         # Drop the timeframe and pose data
#         df = df.iloc[start_idx:end_idx,1:127]

#         if sum(np.isnan(df.to_numpy())) != 0:
#             print('FAIL: na value found')
#             print(df)

#         # normalize
#         data = df.fillna(0).to_numpy()
#         x = np.linspace(0, len(data.T[0]), self.shape[0], endpoint=False)
#         norm_data = np.array([np.interp(x, np.arange(len(col)), col) for col in data.T]).T
#         print(norm_data.shape)
#         norm_data = np.reshape(norm_data, self.shape)
#         print(norm_data.shape)

        # normalize x and y positions based on the width of the shoulders and height from shoulders to nose
#         x1,y1,x2,y2 = df[['pose_11_x','pose_0_y','pose_12_x','pose_12_y']].mean()
        df_array = df.to_numpy().T  # shape: (202,num_frames)
#         col_indices = [df.columns.get_loc(col) for col in ('pose_11_x','pose_0_y','pose_12_x','pose_12_y')]
#         x1,y1,x2,y2 = df_array[col_indices].mean(axis=1)

        for h in ['left','right']:
            x1,y1,x2,y2 = df.filter(regex=h).filter(regex='_x').min().min(),df.filter(regex=h).filter(regex='_y').min().min(),df.filter(regex=h).filter(regex='_x').max().max(),df.filter(regex=h).filter(regex='_y').max().max()
            x_cols = [df.columns.get_loc(col) for col in df.filter(regex=h).filter(regex='_x').columns]
            y_cols = [df.columns.get_loc(col) for col in df.filter(regex=h).filter(regex='_y').columns]
            df_array[x_cols] = (df_array[x_cols]-min(x1,x2))/(max(x1,x2)-min(x1,x2)+0.000001)
            df_array[y_cols] = (df_array[y_cols]-min(y1,y2))/(max(y1,y2)-min(y1,y2)+0.000001)

# #         def norm_pts(p):
# #             px = (p[0]-min(x1,x2))/(max(x1,x2)-min(x1,x2)+0.000001)
# #             py = (p[1]-min(y1,y2))/(max(y1,y2)-min(y1,y2)+0.000001)
# #             return (px,py)
#         x_cols = [df.columns.get_loc(col) for col in df.filter(regex='_x').columns]
#         y_cols = [df.columns.get_loc(col) for col in df.filter(regex='_y').columns]
#         df_array[x_cols] = (df_array[x_cols]-min(x1,x2))/(max(x1,x2)-min(x1,x2)+0.000001)
#         df_array[y_cols] = (df_array[y_cols]-min(y1,y2))/(max(y1,y2)-min(y1,y2)+0.000001)
# #         df_x = (df.filter(regex='_x')-min(x1,x2))/(max(x1,x2)-min(x1,x2)+0.000001)
# #         df_y = (df.filter(regex='_y')-min(y1,y2))/(max(y1,y2)-min(y1,y2)+0.000001)
        norm_df = pd.DataFrame(data=df_array.T, columns=df.columns)
    
        # Drop the frames in the beginning and end of the video where no hands are detected
        # Drop the timeframe and pose data
        start_idx = (~norm_df['lefthand_0_x'].isna() | ~norm_df['righthand_0_x'].isna()).argmax()
        end_idx = len(norm_df) - (norm_df[::-1]['lefthand_0_x'].isna() & norm_df[::-1]['righthand_0_x'].isna()).argmin()
        
        norm_df = norm_df.iloc[start_idx:end_idx,1:127]

        # Fill empty values with the previous seen value
        norm_df = norm_df.fillna(method='ffill').fillna(method='bfill').fillna(0.)
        
        # For classifiers, just return the mean of each column
        return norm_df.mean().to_numpy()

        # for now, just choose 10 frames from the middle
#         data = df.iloc[len(df)//3:len(df)//3+10].mean().to_numpy()
#         if sum(np.isnan(data)) != 0:
#             print(sum(np.isnan(data)))
#         norm_data = np.reshape(data, self.shape)
#         assert data.shape == self.shape
#         return data
    
    def generate_more_data(self, df_array, n=10, std=0.1):
        '''
        Generate more data from a single sample by adding noise
        '''
        samples = []
        
        for i in range(n):
            noise = np.random.normal(0, std, df_array.shape)
            samples.append(df_array + noise)

        return samples


if __name__ == "__main__":
    webcam = WebcamHandler()
    # webcam.stream_webcam()
    webcam.evaluate_model(show=(len(sys.argv) > 1 and sys.argv[1] == '--show'))
