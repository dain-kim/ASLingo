# Data Collection



## Data csv format

| timestamp | lefthand_0_x | ...  | lefthand_20_z | righthand_0_x | ...  | righthand_20_z | pose_0_x | ...  | pose_24_z |
| --------- | ------------ | ---- | ------------- | ------------- | ---- | -------------- | -------- | ---- | --------- |
| 0.0       |              |      |               |               |      |                |          |      |           |

1 + 21 * 3 * 2 + 25 * 3 = **202** columns, **num_frames** rows

Data columns are named in the format "type_idx_coord", where:

- **type** is one of `lefthand`, `righthand`, `pose`
- **idx** is the joint index as defined in MediaPipe (see [hand landmarks indices](https://google.github.io/mediapipe/images/mobile/hand_landmarks.png) and [upper body landmarks indices](https://google.github.io/mediapipe/images/mobile/pose_tracking_upper_body_landmarks.png))
- **coord** is one of `x`, `y`, `z`

## Metadata json format

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

