import json
import os.path
import pathlib

import scenedetect
from datetime import datetime
from utils import s3_utils

cwd = pathlib.Path(__file__).parent


def to_timecode(timecode):
    time_format = "%H:%M:%S:%f"
    time_object = datetime.strptime(timecode, time_format)

    # Calculate fractional milliseconds
    fractional_milliseconds = int(time_object.microsecond / 1000)

    # Format the result as HH:MM:SS.nnnn
    formatted_result = f"{time_object.hour:02d}:{time_object.minute:02d}:{time_object.second:02d}.{fractional_milliseconds:04d}"

    return formatted_result


class PySceneUtil:

    # TODO: Need to remove static file path
    def __init__(self, video_file_name, rekognition_json, scene_threshold, min_scene_length):
        self.video_file_name = video_file_name
        self.video_path = os.path.join(cwd.parent, f'video/{video_file_name}')
        self.rekognition_json = rekognition_json
        self.detector = scenedetect.ContentDetector(threshold=scene_threshold, min_scene_len=min_scene_length)

    def filter_rekognition_json(self):
        filtered_data = []
        for d in self.rekognition_json:
            shot_dict = {
                "DurationMillis": d['DurationMillis'],
                "StartTimecodeSMPTE": d['StartTimecodeSMPTE'],
                "EndTimecodeSMPTE": d['EndTimecodeSMPTE'],
                "Type": d["Type"]}
            filtered_data.append(shot_dict)
        i = 0
        for d in filtered_data:
            if d['DurationMillis'] < 1500:
                if i == 0 or filtered_data[i - 1]['DurationMillis'] < 1500:
                    filtered_data[i + 1]['DurationMillis'] += filtered_data[i]['DurationMillis']
                    filtered_data[i + 1]['StartTimecodeSMPTE'] = filtered_data[i]['StartTimecodeSMPTE']
                else:
                    filtered_data[i - 1]['DurationMillis'] += filtered_data[i]['DurationMillis']
                    filtered_data[i - 1]['EndTimecodeSMPTE'] = filtered_data[i]['EndTimecodeSMPTE']
            i += 1
        filtered_data = [d for d in filtered_data if d['DurationMillis'] > 1500]
        for index, item in enumerate(filtered_data):
            item['Index'] = index
        # print(len(filtered_data))
        print(json.dumps(filtered_data))
        return filtered_data

    # TODO: Format results into JSON and store into S3
    # TODO: Delete the video file once the processing ends

    def start_detection(self):
        s3_utils.download_file(self.video_file_name)
        shots = self.filter_rekognition_json()
        for shot in shots:
            start = to_timecode(shot['StartTimecodeSMPTE'])
            end = to_timecode(shot['EndTimecodeSMPTE'])
            result = scenedetect.detect(self.video_path, detector=self.detector, start_time=start, end_time=end)
            if len(result) == 0:
                continue
            index = 0
            subshots = []
            for r in result:
                s = r[0].get_timecode()
                e = r[1].get_timecode()
                if s == e:
                    continue
                subshot_dict = {
                    "index": index,
                    "Type": "SUBSHOT",
                    "StartTimeCode": s,
                    "EndTimeCode": e
                }
                index += 1
                subshots.append(subshot_dict)
            shot["Subshots"] = subshots
        return shots
