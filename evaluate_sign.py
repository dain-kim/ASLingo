import sys
import cv2
import numpy as np
import pandas as pd
import string
import time
# from keras.models import load_model  # This line causes a weird bug!!
# import keras
import mediapipe as mp
from data_collection import get_mediapipe_results, process_video, parse_data, get_image_overlay

sampled_words = ['LETTER-'+let for let in string.ascii_uppercase]
from sklearn import preprocessing
encoder = preprocessing.LabelEncoder()
encoder.fit(sampled_words)

# letters only for now
# from keras.models import load_model
# model = load_model('cnn_letters_1.h5')


# load the model from disk
import pickle
with open('lda_letters_static_hand.pkl', 'rb') as f:
    model = pickle.load(f)


# def preprocess(df):
#     '''
#     just the cleanup: cut out head and tail, fill nan, normalize
#     '''
#     # Drop the frames in the beginning and end of the video where no hands are detected
#     start_idx = (~df['lefthand_0_x'].isna() | ~df['righthand_0_x'].isna()).argmax()
#     end_idx = len(df) - (df[::-1]['lefthand_0_x'].isna() & df[::-1]['righthand_0_x'].isna()).argmin()
#     # df = df.iloc[start_idx:end_idx]
#     # for lda
#     df = df.iloc[start_idx:end_idx,1:]
    
#     # Fill empty values with the previous seen value
#     df = df.fillna(method='ffill')
#     df = df.fillna(method='bfill')

#     return df

# def normalize(df, num_rows=50):
#     # # Test 1: mean and std of each column
#     # m = np.array(df.iloc[:,1:].mean().fillna(0))
#     # s = np.array(df.iloc[:,1:].std().fillna(0))
#     # norm_data = np.concatenate((m,s))
#     # return norm_data

#     # Test 2: normalize to fixed number of rows
#     # data is 2D (time and position), so model needs to be cnn
#     data = df.fillna(0).to_numpy()
#     x = np.linspace(0, len(data.T[0]), num_rows, endpoint=False)
#     norm_data = np.array([np.interp(x, np.arange(len(col)), col) for col in data.T]).T
#     return norm_data

# # live data
# def buffer_generator(cap, buffer_size=50, sliding_window=10):
#     print('buffer generator')
#     if sliding_window > buffer_size:
#         sliding_window = buffer_size
#     framecount = 0
#     timestamps = []
#     hand_results = []
#     pose_results = []

#     # cap = cv2.VideoCapture(0)
#     while cap.isOpened():
#         success, image = cap.read()
#         if success:
#             framecount += 1
#         else:
#             # If loading from webcam, use 'continue' instead of 'break'.
#             continue

#         hand_result, pose_result = get_mediapipe_results(image)
#         hand_results.append(hand_result)
#         pose_results.append(pose_result)
#         timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))

#         # show
#         # image.flags.writeable = True
#         # # ...

#         if framecount % buffer_size == 0:
#             # print('reached buffer of size ',buffer_size, framecount%buffer_size)
#             # print('sanity check: buffer length', len(hand_results), 'reached', buffer_size)
#             yield {'timestamps': timestamps,
#                    'hand_results': hand_results,
#                    'pose_results': pose_results}
#             timestamps = timestamps[sliding_window:]
#             hand_results = hand_results[sliding_window:]
#             pose_results = pose_results[sliding_window:]

#         elif framecount % sliding_window == 0:
#             # print('sanity check: buffer length', len(hand_results), '=', buffer_size)
#             yield {'timestamps': timestamps,
#                    'hand_results': hand_results,
#                    'pose_results': pose_results}
#             timestamps = timestamps[sliding_window:]
#             hand_results = hand_results[sliding_window:]
#             pose_results = pose_results[sliding_window:]


#     cap.release()

class WebcamHandler(object):
    def __init__(self):
        # self.cap = cap
        self.cap = None
        self.image = None
        self.processor = StaticSignProcessor((126,))
        self.timestamps = []
        self.hand_results = []
        self.pose_results = []
        self.framecount = 0

    def process_frame(self, frame, buffer_size=50, sliding_window=10):
        # if self.cap.isOpened():
        #     success, image = self.cap.read()
        #     if not success:
        #         return

        hand_result, pose_result = get_mediapipe_results(frame)
        if not hand_result.multi_handedness:
            # print('no hands detected')
            self.timestamps = []
            self.hand_results = []
            self.pose_results = []
            self.framecount = 0
            return

        self.framecount += 1
        self.hand_results.append(hand_result)
        self.pose_results.append(pose_result)
        # self.timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
        # time is a construct
        self.timestamps.append(0.0)

        # if show:
        #     image.flags.writeable = True
        #     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        #     mp_drawing.draw_landmarks(
        #         image, pose_result.pose_landmarks, mp_pose.UPPER_BODY_POSE_CONNECTIONS)
        #     if hand_result.multi_hand_landmarks:
        #         for hand_landmarks in hand_result.multi_hand_landmarks:
        #             mp_drawing.draw_landmarks(
        #                 image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        #     cv2.imshow('MediaPipe Processed Video', image)
        #     if cv2.waitKey(5) & 0xFF == 27:
        #         break
            # ...

        if self.framecount % buffer_size == 0:
            # print('reached buffer of size ',buffer_size, self.framecount%buffer_size)
            # print('sanity check: buffer length', len(self.hand_results), '=', buffer_size)
            buf = {'timestamps': self.timestamps,
                   'hand_results': self.hand_results,
                   'pose_results': self.pose_results}
            self.timestamps = self.timestamps[sliding_window:]
            self.hand_results = self.hand_results[sliding_window:]
            self.pose_results = self.pose_results[sliding_window:]
            return buf

        elif self.framecount % sliding_window == 0 and self.framecount > buffer_size:
            # print('sanity check: buffer length', len(self.hand_results), '=', buffer_size)
            buf = {'timestamps': self.timestamps,
                   'hand_results': self.hand_results,
                   'pose_results': self.pose_results}
            self.timestamps = self.timestamps[sliding_window:]
            self.hand_results = self.hand_results[sliding_window:]
            self.pose_results = self.pose_results[sliding_window:]
            return buf

    def stream_webcam(self):
        self.cap = cv2.VideoCapture(0)
        while self.cap.isOpened():
            success, image = self.cap.read()
            if success:
                image,_,_ = self.get_frame(image)
                cv2.imshow('webcam', image)
                # if webcam.framecount % 10 == 0:
                #     print(webcam.framecount)
                # cv2.waitKey(0)
                # print(time.time()-s)
            if cv2.waitKey(5) & 0xFF == 27:
                print('esc')
                break

        self.cap.release()
        self.cap = None

    def get_next_frame(self, return_pred=False):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            success, image = self.cap.read()
            if success:
                image, pred, score = self.get_frame(image)
            if return_pred:
                return success, image, pred, score
            return success, image

    def get_frame(self, image, pred_thresh=0.3):
        score = ''
        prediction = ''
        s = time.time()
        gen_buffer = self.process_frame(image, buffer_size=10, sliding_window=1)
        if gen_buffer:
            # parsed = parse_data(gen_buffer)
            # X_data = normalize(preprocess(parsed))
            # X_data = np.reshape(X_data, (1, 50, 201, 1))
            parsed = parse_data(gen_buffer)
            X_data = self.processor.process(parsed)

            # pred = model.predict(np.array([X_data]))
            start = time.time()
            pred_prob = model.predict_proba([X_data])[0]
            # print(encoder.inverse_transform([pred_class]))
            # pred_prob = pred[0]
            pred_class = list(pred_prob).index(max(pred_prob))
            if max(pred_prob) < pred_thresh:
                print('PREDICTED: NEUTRAL', max(pred_prob))
                # prediction = None
            else:
                # print('PREDICTED:', pred_class_to_letter(pred_class)[0], max(pred_prob))
                prediction = pred_class_to_letter(pred_class)[0]
                score = str(round(max(pred_prob),2))
            # print('PREDICTED:', pred_class_to_letter(pred)[0])
            pred_class = list(pred_prob).index(max(pred_prob))
            
        if self.hand_results:
            image = get_image_overlay(image, self.hand_results[-1], self.pose_results[-1])
        else:
            prediction = 'No hands detected'
        image = cv2.flip(image, 1)
        if prediction:
            cv2.putText(image, prediction + '  ' + score, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)


        return image, prediction, score



# def evaluate_sign_from_recording(video_path):
#     processed = process_video(video_path, show=False)
#     # print('processed')
#     parsed = parse_data(processed)
#     # print('parsed')

#     X_data = normalize(preprocess(parsed))
#     # print('normalized')
#     X_data = np.reshape(X_data, (1, 50, 201, 1))
#     # print(X_data.shape)

#     # # letters only for now
#     # from keras.models import load_model
#     # model = load_model('cnn_letters_1.h5')
#     # print('model loaded')
#     pred = model.predict(X_data)
#     pred_prob = pred[0]
#     pred_class = list(pred_prob).index(max(pred_prob))
#     print('PREDICTED:', pred_class_to_letter(pred_class))
#     return pred

def pred_class_to_letter(pred_class):
    return encoder.inverse_transform(np.array([pred_class]))

class StaticSignProcessor():
    def __init__(self, X_shape=(10,126,1)):
        self.shape = X_shape
    
    def process(self, df):
        '''
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

# def get_frame(image, pred_thresh=0.3):
#     score = ''
#     prediction = None
#     s = time.time()
#     gen_buffer = webcam(image, buffer_size=10, sliding_window=1)
#     if gen_buffer:
#         # parsed = parse_data(gen_buffer)
#         # X_data = normalize(preprocess(parsed))
#         # X_data = np.reshape(X_data, (1, 50, 201, 1))
#         parsed = parse_data(gen_buffer)
#         X_data = processor.process(parsed)

#         # pred = model.predict(np.array([X_data]))
#         start = time.time()
#         pred_prob = model.predict_proba([X_data])[0]
#         # print(encoder.inverse_transform([pred_class]))
#         # pred_prob = pred[0]
#         pred_class = list(pred_prob).index(max(pred_prob))
#         if max(pred_prob) < pred_thresh:
#             print('PREDICTED: NEUTRAL', max(pred_prob))
#             # prediction = None
#         else:
#             print('PREDICTED:', pred_class_to_letter(pred_class)[0], max(pred_prob))
#             prediction = pred_class_to_letter(pred_class)[0]
#             score = str(round(max(pred_prob),2))
#         # print('PREDICTED:', pred_class_to_letter(pred)[0])
#         pred_class = list(pred_prob).index(max(pred_prob))
        
#     if webcam.hand_results:
#         image = get_image_overlay(image, webcam.hand_results[-1], webcam.pose_results[-1])
#     else:
#         prediction = 'No hands detected'
#     image = cv2.flip(image, 1)
#     if prediction:
#         cv2.putText(image, prediction + '  ' + score, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)


#     return image
    

# def stream_webcam():
#     cap = cv2.VideoCapture(0)
#     while cap.isOpened():
#         success, image = cap.read()
#         if success:
            
#             image = get_frame(image)
#             cv2.imshow('webcam', image)
#             # if webcam.framecount % 10 == 0:
#             #     print(webcam.framecount)
#             # cv2.waitKey(0)
#             # print(time.time()-s)
#         if cv2.waitKey(5) & 0xFF == 27:
#             print('esc')
#             break
#     cap.release()

    

if __name__ == "__main__":
    # for i,let in enumerate(string.ascii_uppercase):
    #     idx = 26710 + i
    #     vid_path = 'https://www.signingsavvy.com/media/mp4-ld/26/{}.mp4'.format(idx)
    #     # vid_path = 'test_webcam_data/'+let+'.mp4'
    #     print('evaluating letter', vid_path)
    #     evaluate_sign_from_recording(vid_path)
    # process_video(sys.argv[1], show=False)

    # evaluate_sign_from_recording(sys.argv[1])
    # start = time.time()
    webcam = WebcamHandler()
    # processor = StaticSignProcessor((126,))
    webcam.stream_webcam()

    # vid_src = 'https://aslsignbank.haskins.yale.edu/dictionary/protected_media/glossvideo/ASL/LE/LETTER-X-1654.mp4'
    # vid_src = sys.argv[1]
    # vid_src = 'test_webcam_data/test_webcam_data.mp4'
    # stream_webcam()



    # cap = cv2.VideoCapture(0)
    # while cap.isOpened():
    #     success, image = cap.read()
    #     prediction = None
    #     # print(cv2.CAP_PROP_FPS)
    #     score = ''
    #     if success:
    #         s = time.time()
    #         gen_buffer = webcam(image, buffer_size=10, sliding_window=1)
    #         if gen_buffer:
    #             # parsed = parse_data(gen_buffer)
    #             # X_data = normalize(preprocess(parsed))
    #             # X_data = np.reshape(X_data, (1, 50, 201, 1))
    #             parsed = parse_data(gen_buffer)
    #             X_data = processor.process(parsed)

    #             # pred = model.predict(np.array([X_data]))
    #             start = time.time()
    #             pred_prob = model.predict_proba([X_data])[0]
    #             # print(encoder.inverse_transform([pred_class]))
    #             # pred_prob = pred[0]
    #             pred_class = list(pred_prob).index(max(pred_prob))
    #             if max(pred_prob) < 0.3:
    #                 print('PREDICTED: NEUTRAL', max(pred_prob))
    #                 # prediction = None
    #             else:
    #                 print('PREDICTED:', pred_class_to_letter(pred_class)[0], max(pred_prob))
    #                 prediction = pred_class_to_letter(pred_class)[0]
    #                 score = str(round(max(pred_prob),2))
    #             # print('PREDICTED:', pred_class_to_letter(pred)[0])
    #             pred_class = list(pred_prob).index(max(pred_prob))
                
    #         if webcam.hand_results:
    #             image = get_image_overlay(image, webcam.hand_results[-1], webcam.pose_results[-1])
    #         else:
    #             prediction = 'No hands detected'
    #         image = cv2.flip(image, 1)
    #         if prediction:
    #             cv2.putText(image, prediction + '  ' + score, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
    #         cv2.imshow('webcam', image)
    #         # if webcam.framecount % 10 == 0:
    #         #     print(webcam.framecount)
    #         # cv2.waitKey(0)
    #         print(time.time()-s)
    #         if cv2.waitKey(5) & 0xFF == 27:
    #             print('esc')
    #             break
    #     # buffer_generator(cap)
    #     # get_image_overlay(image, webcam.hand_results[-1], webcam.pose_results[-1])

    # cap.release()


