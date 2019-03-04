import os
from pathlib import Path
import json
from pprint import pprint


def list_video_names(videos_path, video_list_file):
    """
    Creates a file containing the list of all the video names for the videos in 'video_path'
    """
    with open(video_list_file, 'w') as f:
        p = Path(videos_path)
        for path in p.glob('*.avi'):
            video_path = str(path)
            video_name = (video_path.split('/')[-1]).split('.')[0]
            f.write(video_name + '\n')

if __name__ == "__main__":
    # folder that contains all the video that have been treated by OpenPose
    videos_path = 'video'
    # folder that contains all the JSON files generated by OpenPose (for all the frames of all the videos)
    openpose_json_path = 'openpose_json'
    # folder that will contain the converted files (one per video)
    stgcn_json_path =  'st-gcn_format/'
    # file that will contain the list of all the video file names that were treated by OpenPose
    video_list_file = 'data_list.dat'
    # file that will contain the labels for each video
    labels_file = 'fake_labels.json'
    list_video_names(videos_path, video_list_file)
    p = Path(openpose_json_path)
    
    labels = {}
    with open(video_list_file, 'r') as f:
        for line in f:
            video_name  = line.strip('\n')
            stgcn_data_array = []
            stgcn_data = {}
            dest_path = stgcn_json_path + video_name + '.json'
            for path in p.glob(video_name + '*.json'): # each json file for this video
                json_path = str(path)
                frame_id = int(((json_path.split('/')[-1]).split('.')[0]).split('_')[1])
                frame_data = {'frame_index': frame_id}
                data = json.load(open(json_path))
                skeletons = []        
                for person in data['people']:
                    score, coordinates = [], []
                    skeleton = {}
                    keypoints = person['pose_keypoints_2d']
                    for i in range(0, len(keypoints), 3):
                        coordinates +=  [keypoints[i], keypoints[i + 1]]
                        score += [keypoints[i + 2]]
                    skeleton['pose'] = coordinates
                    skeleton['score'] = score
                    skeletons += [skeleton]
                frame_data['skeleton'] = skeletons
                stgcn_data_array += [frame_data]

            labels[video_name] = {"has_skeleton": True, 
                "label": "fake_label", 
                "label_index": 0}
            stgcn_data['data'] = stgcn_data_array
            stgcn_data['label'] = 'fake_label'
            stgcn_data['label_index'] = 0
            with open(dest_path, 'w') as outfile:
                json.dump(stgcn_data, outfile)

    with open(labels_file, 'w') as label_file:
        json.dump(labels, label_file)