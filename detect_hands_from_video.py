# base code source: https://google.github.io/mediapipe/solutions/hands.html#python-solution-api
import sys
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def detect_hands_from_video(video_path, show=True):
    cap = cv2.VideoCapture(video_path)
    timestamps = []
    results = []
    with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                # If loading from webcam, use 'continue' instead of 'break'.
                break
            timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))

            # Flip image around y-axis for correct handedness output.
            image = cv2.flip(image, 1)
            # Convert the BGR image to RGB.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            result = hands.process(image)
            results.append(result)

            # Draw the hand annotations on the image.
            if show:
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if result.multi_hand_landmarks:
                    for hand_idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
                        if result.multi_handedness[hand_idx].classification[0].label == 'Right':
                            mp_drawing.draw_landmarks(
                                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        else:
                            mp_drawing.draw_landmarks(
                                image, hand_landmarks)
                cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                    break
    cap.release()

    return [timestamps, results]

if __name__ == "__main__":
    detect_hands_from_video(sys.argv[1])