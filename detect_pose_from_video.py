# base code source: https://google.github.io/mediapipe/solutions/pose.html#python-solution-api
import sys
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def detect_pose_from_video(video_path, show=True):
    cap = cv2.VideoCapture(video_path)
    timestamps = []
    results = []
    with mp_pose.Pose(
        upper_body_only=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                # If loading a video, use 'break' instead of 'continue'.
                break
            timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))

            # Flip image around y-axis for correct handedness output.
            image = cv2.flip(image, 1)
            # Convert the BGR image to RGB.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            result = pose.process(image)
            results.append(result)

            # Draw the pose annotation on the image.
            if show:
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                mp_drawing.draw_landmarks(
                    image, result.pose_landmarks, mp_pose.UPPER_BODY_POSE_CONNECTIONS)
                cv2.imshow('MediaPipe Pose', image)
                if cv2.waitKey(5) & 0xFF == 27:
                    break
    cap.release()

    return [timestamps, results]    

if __name__ == "__main__":
    detect_pose_from_video(sys.argv[1])