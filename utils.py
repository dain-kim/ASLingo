import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
import string
from sklearn import preprocessing
# from SignBankRefIDs import SB_REF_IDS
# from requests_html import HTMLSession


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
one_hand = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
pose = mp_pose.Pose(
    upper_body_only=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

def mp_process_image(image, num_hands=1):
    # Flip image around y-axis for correct handedness output.
    image = cv2.flip(image, 1)
    # Convert the BGR image to RGB.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable.
    image.flags.writeable = False
    if num_hands == 2:
        hand_result = hands.process(image)
    else:
        hand_result = one_hand.process(image)
    pose_result = pose.process(image)

    return [hand_result, pose_result]

def mp_process_video(video_src, num_hands=2, show=False):
    '''
    Process hand and pose information from video source using mediapipe.
    Returns:
    A dict containing timestamps, hand_results, and pose_results
    '''
    cap = cv2.VideoCapture(video_src)
    timestamps = []
    hand_results = []
    pose_results = []

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            # If loading from webcam, use 'continue' instead of 'break'.
            break

        timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
        hand_result, pose_result = mp_process_image(image, num_hands=num_hands)

        hand_results.append(hand_result)
        pose_results.append(pose_result)

        # Draw the hand and pose annotations on the image.
        if show:
            image = annotate_image(image, hand_result, pose_result)
            cv2.imshow('MediaPipe Processed Video', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    return {'timestamps': timestamps,
            'hand_results': hand_results,
            'pose_results': pose_results}

def annotate_image(image, hand_result, pose_result):
    image.flags.writeable = True
    image = cv2.flip(image, 1)

    mp_drawing.draw_landmarks(
        image, pose_result.pose_landmarks, mp_pose.UPPER_BODY_POSE_CONNECTIONS)
    if hand_result.multi_hand_landmarks:
        for hand_landmarks in hand_result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    image = cv2.flip(image, 1)
    return image

def generate_dataframe(processed):
    '''
    Parses the dict containing timestamps, hand_results, and pose_results
    and returns a pd DataFrame object of shape (num_frames, 202).
    '''
    timestamps = processed['timestamps']
    hand_results = processed['hand_results']
    pose_results = processed['pose_results']

    data = []

    # Get hand and pose data for each frame and append the combined array to data
    for frame_idx in range(len(timestamps)):
        hand_data = hand_results[frame_idx]
        pose_data = pose_results[frame_idx]

        # Initialize the 2 x 63 hand array
        hand_coords = np.array([[np.nan] * len(mp_hands.HAND_CONNECTIONS) * 3] * 2)

        if hand_data.multi_handedness:
            # Resolve cases where two hands are detected but they are classified as both left or both right
            if len(hand_data.multi_handedness) == 2 and \
                hand_data.multi_handedness[0].classification[0].label == hand_data.multi_handedness[1].classification[0].label:
                # For now, arbitrarily set the first one as left and second as right
                # Possible improvement here is to infer the correct classification based on previous frames
                hand_data.multi_handedness[0].classification[0].label = 'Left'
                hand_data.multi_handedness[1].classification[0].label = 'Right'

            for hand_idx, hand_landmarks in enumerate(hand_data.multi_hand_landmarks):
                handedness = 0 if hand_data.multi_handedness[hand_idx].classification[0].label == 'Left' else 1
                hand_coords[handedness] = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()

        hand_coords = hand_coords.flatten()

        # Initialize the 1 x 75 pose array
        pose_coords = np.array([np.nan] * len(mp_pose.UPPER_BODY_POSE_CONNECTIONS) * 3)

        if pose_data.pose_landmarks:
            pose_coords = np.array([[lm.x, lm.y, lm.z] for lm in pose_data.pose_landmarks.landmark]).flatten()

        frame_data = np.append([timestamps[frame_idx]], np.append(hand_coords, pose_coords))
        data.append(frame_data)

    data = np.array(data)
    columns = ['timestamps'] + \
            [_type+'_'+str(idx)+'_'+coord \
                for _type in ['lefthand','righthand'] \
                for idx in range(len(mp_hands.HAND_CONNECTIONS)) \
                for coord in ['x','y','z']] + \
            ['pose_'+str(idx)+'_'+coord \
                for idx in range(len(mp_pose.UPPER_BODY_POSE_CONNECTIONS)) \
                for coord in ['x','y','z']]
    df = pd.DataFrame(data=data, columns=columns)
    return df

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


    def flip_hands(self, df_array):
        assert len(df_array) == 126
        return np.concatenate((df_array[len(df_array)//2:],df_array[:len(df_array)//2]))
    
    def generate_more_data(self, df_array, n=10, std=0.1):
        '''
        Generate more data from a single sample by adding noise
        '''
        samples = []
        
        for i in range(n):
            noise = np.random.normal(0, std, df_array.shape)
            # randomly select up to 5 joints to perturb
            perturb_indices = np.random.choice(len(df_array.T), np.random.choice(5), replace=False)
            df_array.T[perturb_indices] = df_array.T[perturb_indices] + np.random.normal(0, std, df_array.T[perturb_indices].shape)
            samples.append(df_array + noise)

        return samples


sampled_words = ['LETTER-'+let for let in string.ascii_uppercase]
encoder = preprocessing.LabelEncoder()
encoder.fit(sampled_words)

def pred_class_to_letter(pred_class):
    return encoder.inverse_transform(np.array([pred_class]))

################## OLD STUFF ###################

def mediapipe_idx_parser(idx, mode='hand'):
    if mode == 'hand':
        return str(mp_hands.HandLandmark(idx)).split('.')[-1]
    elif mode == 'pose':
        return str(mp_pose.PoseLandmark(idx)).split('.')[-1]

# BASE_URL = "https://aslsignbank.haskins.yale.edu"
# VIDEO_URL = BASE_URL + "/dictionary/protected_media/glossvideo/ASL/"
# AJAX_URL = BASE_URL + "/dictionary/ajax/glossrow/"
# session = HTMLSession()

# deprecated
def request_video_info(ref_id):
    '''
    Returns:
    A dict in the format {'video_path': 'fake/url', 'word': 'HELLO', 'synonyms': ['hi', 'hey']},
    or None if video url cannot be accessed
    '''
    try:
        r = session.get(AJAX_URL+str(ref_id))
        if r.status_code == 200:
            video_path = BASE_URL + r.html.find('video')[0].attrs['src']
            word = r.html.find('td')[2].text
            synonyms = r.html.find('td')[3].text.split(', ')
            return {'video_path': video_path,
                    'word': word,
                    'synonyms': synonyms}
        else:
            print('Cannot get url {}'.format(AJAX_URL+str(ref_id)))
    except:
        print('Could not find video at {}'.format(AJAX_URL+str(ref_id)))



def generate_video_urls_from_signdata():
    # signdata.csv is downloaded from here: https://asl-lex.org
    df = pd.read_csv('signdata.csv')
    df = df[['SignBankLemmaID','SignBankReferenceID']].dropna()
    df['VideoUrl'] = VIDEO_URL + (df['SignBankLemmaID'].astype(str)+'-').str[:2] + '/' + df['SignBankLemmaID'] + '-' + df['SignBankReferenceID'].astype(int).astype(str) + '.mp4'

    for url in list(df['VideoUrl']):
        cap = cv2.VideoCapture(url)


def collect_signbank_data(start_from):
    for i, ref_id in enumerate(SB_REF_IDS[start_from:]):
        print(start_from+i, 'ref id', ref_id)
        # Get video url and word information
        try:
            video_metadata = request_video_info(ref_id)
            if video_metadata:
                # Process video with mediapipe to get hand and pose data
                processed = process_video(video_metadata['video_src'], show=False)
                # Parse mediapipe data into csv format
                dataframe = parse_data(processed)
                # Save data
                save_parsed_data(video_metadata, dataframe)
        except:
            print('ERROR: failed to save data for ref id', ref_id)
