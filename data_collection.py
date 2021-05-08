import os
import json
from letters_dict import letter_vids
from utils import mp_process_video, generate_dataframe


def save_parsed_data(video_metadata, dataframe):
    '''
    Save the video information and metadata in two separate files.
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

def collect_data():
    if os.path.exists('data'):
        print('data folder already exists. continue? y/[n]')
        if input().lower() != 'y':
            return

    for letter in letter_vids:
        print('Collecting data for:', letter)
        for video_src in letter_vids[letter]:
            # Process video with mediapipe to get hand and pose data
            processed = mp_process_video(video_src, num_hands=1)
            # Parse intermediate mediapipe data into a pd dataframe
            df = generate_dataframe(processed)
            video_metadata = {'word': letter,
                              'synonyms': [],
                              'video_src': video_src}
            # Save data
            save_parsed_data(video_metadata, df)


if __name__ == "__main__":
    collect_data()
