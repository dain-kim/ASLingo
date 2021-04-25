# hand detection base code source: 
# https://google.github.io/mediapipe/solutions/hands.html#python-solution-api
# pose detection base code source: 
# https://google.github.io/mediapipe/solutions/pose.html#python-solution-api
import cv2
import sys
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
hands = mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
pose = mp_pose.Pose(
    upper_body_only=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

def mediapipe_idx_parser(idx, mode='hand'):
    if mode == 'hand':
        return str(mp_hands.HandLandmark(idx)).split('.')[-1]
    elif mode == 'pose':
        return str(mp_pose.PoseLandmark(idx)).split('.')[-1]



# def generate_video_urls_from_signdata():
#     # signdata.csv is downloaded from here: https://asl-lex.org
#     df = pd.read_csv('signdata.csv')
#     df = df[['SignBankLemmaID','SignBankReferenceID']].dropna()
#     df['VideoUrl'] = VIDEO_URL + (df['SignBankLemmaID'].astype(str)+'-').str[:2] + '/' + df['SignBankLemmaID'] + '-' + df['SignBankReferenceID'].astype(int).astype(str) + '.mp4'

#     for url in list(df['VideoUrl']):
#         cap = cv2.VideoCapture(url)


if __name__ == "__main__":
    process_video(sys.argv[1])
