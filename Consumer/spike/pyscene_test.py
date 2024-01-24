import json

import scenedetect
from datetime import datetime

video_path = '../video/ALADDIN_TLR-1_1920x800_PDA_51-thedigitaltheater(1).mp4'


def detect_scenes(start_time, end_time):
    detector = scenedetect.ContentDetector(threshold=20, min_scene_len=60)
    # Detect all scenes in video from current position to end.
    data = scenedetect.detect(video_path, detector=detector, start_time=start_time, end_time=end_time)
    # `get_scene_list` returns a list of start/end timecode pairs
    # for each scene that was found.
    return data


# TODO: Merge the interval of times. Say shot 4 has end time 00::00::04:34 and shot 5 has end time as 00::00::06:21
#  and we want to eliminate shot 5 then make shot 4's end time as 00::00::06:21
def filter_json():
    rekognition_json_path = '../json/ALADDIN_TLR-1_1920x800_PDA_51-thedigitaltheater(1).json'
    with open(rekognition_json_path, 'r') as rekognition_json:
        data = json.load(rekognition_json)
        # print(len(data))

        # Taking only the scenes whose duration is more than 1.5 seconds
        # filtered_data = [d for d in data if d['DurationMillis'] > 1500]
        filtered_data = []
        for d in data:
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


def to_timecode(timecode):
    time_format = "%H:%M:%S:%f"
    time_object = datetime.strptime(timecode, time_format)

    # Calculate fractional milliseconds
    fractional_milliseconds = int(time_object.microsecond / 1000)

    # Format the result as HH:MM:SS.nnnn
    formatted_result = f"{time_object.hour:02d}:{time_object.minute:02d}:{time_object.second:02d}.{fractional_milliseconds:04d}"

    return formatted_result


if __name__ == '__main__':

    shots = filter_json()
    for shot in shots:
        start = to_timecode(shot['StartTimecodeSMPTE'])
        end = to_timecode(shot['EndTimecodeSMPTE'])
        result = detect_scenes(start, end)
        if len(result) == 0:
            continue
        print(f"{shot['Index']} : {shot['StartTimecodeSMPTE']} -> {shot['EndTimecodeSMPTE']}")
        for r in result:
            s = r[0].get_timecode()
            e = r[1].get_timecode()
            print(f"{s} to {e}")
