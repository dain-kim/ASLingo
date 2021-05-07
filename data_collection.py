import cv2
import json
import os, sys
import numpy as np
import pandas as pd
import mediapipe as mp
from requests_html import HTMLSession
from SignBankRefIDs import SB_REF_IDS

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

BASE_URL = "https://aslsignbank.haskins.yale.edu"
VIDEO_URL = BASE_URL + "/dictionary/protected_media/glossvideo/ASL/"
AJAX_URL = BASE_URL + "/dictionary/ajax/glossrow/"
session = HTMLSession()

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

def get_mediapipe_results(image, num_hands=2):
    # Flip image around y-axis for correct handedness output.
    image = cv2.flip(image, 1)
    # Convert the BGR image to RGB.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    if num_hands == 2:
        hand_result = hands.process(image)
    else:
        hand_result = one_hand.process(image)
    pose_result = pose.process(image)

    return [hand_result, pose_result]


def process_video(video_src, show=False, flip=False, num_hands=2):
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
        if flip:
            image = cv2.flip(image, 1)

        timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
        hand_result, pose_result = get_mediapipe_results(image, num_hands=num_hands)

        hand_results.append(hand_result)
        pose_results.append(pose_result)

        # Draw the hand and pose annotations on the image.
        if show:
            image = get_image_overlay(image, hand_result, pose_result)
            cv2.imshow('MediaPipe Processed Video', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()

    return {'timestamps': timestamps,
            'hand_results': hand_results,
            'pose_results': pose_results}

def get_image_overlay(image, hand_result, pose_result):
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

def parse_data(processed):
    '''
    Parse the intermediate mediapipe data objects into a pd DataFrame object
    of shape (num_frames, 202) to be saved into a csv file.
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
            if len(hand_data.multi_handedness) == 2 and hand_data.multi_handedness[0].classification[0].label == hand_data.multi_handedness[1].classification[0].label:
                # For now, arbitrarily set the first one as left and second as right
                # Possible improvement here is to infer the correct classification based on previous frames
                hand_data.multi_handedness[0].classification[0].label = 'Left'
                hand_data.multi_handedness[1].classification[0].label = 'Right'
            # print(hand_data.multi_handedness[0].classification[0].label)

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

def save_parsed_data(video_metadata, dataframe):
    '''
    Save the parsed information and metadata in two separate files.
    The word, video_path, and synonyms from video_metadata is saved in data/metadata.json
    Timestamped hand and pose information is saved in data/[WORD]/[sample_idx].csv
    where sample_idx is a 0-indexed counter for differentiating distinct video samples.
    '''
    if not os.path.isdir('data'):
        os.mkdir('data')

    word = video_metadata['word']
    synonyms = video_metadata['synonyms']
    video_src = video_metadata['video_src']

    # Save video data
    if not os.path.isdir(os.path.join('data', word)):
        os.mkdir(os.path.join('data', word))

    sample_idx = 0
    data_path = os.path.join('data', word, str(sample_idx) + '.csv')
    while os.path.exists(data_path):
        sample_idx += 1
        data_path = os.path.join('data', word, str(sample_idx) + '.csv')

    dataframe.to_csv(data_path, index=False)

    # Save metadata
    metadata = {}
    metadata_path = os.path.join('data', 'metadata.json')
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            metadata = json.load(f)

    entry = {'synonyms': synonyms, 'video_src': {}}
    if metadata.get(word):
        entry = metadata.get(word)

    entry['video_src'][str(sample_idx)] = video_src

    metadata[word] = entry

    to_json = json.dumps(metadata)
    with open(metadata_path, 'w') as f:
        f.write(to_json)
        f.close()


def main(start_from):
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

def letter_augment():
    from letters_dict import letter_vids
    for letter in letter_vids:
        print(letter)
        for video_src in letter_vids[letter]:

            # Process video with mediapipe to get hand and pose data
            processed = process_video(video_src, show=False, num_hands=1)
            # Parse mediapipe data into csv format
            dataframe = parse_data(processed)
            video_metadata = {'word': letter,
                              'synonyms': [],
                              'video_src': video_src}
            # Save data
            save_parsed_data(video_metadata, dataframe)
            # processed = process_video(letter_vids[letter][2], show=True, flip=True, num_hands=1)
            # processed = process_video(video_src, show=True, num_hands=1, flip=True)

        

if __name__ == "__main__":
    # process_video(sys.argv[1])
    # start_from = 0
    # if len(sys.argv) == 2:
    #     start_from = int(sys.argv[1])
    # main(start_from)
    letter_augment()
    # pass
