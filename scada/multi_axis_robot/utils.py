import json
from multi_axis_robot import models
from datetime import datetime

def save_data(multi_axis_robot_dict):

    # Pull out the timestamp and remove from dict
    time_stamp = multi_axis_robot_dict['timestamp']
    # YYYY-MM-DD HH:MM:ss
    updated_timestamp = datetime.strptime( time_stamp, "%m/%d/%Y, %H:%M:%S" )

    del multi_axis_robot_dict['timestamp']

    for key, value in multi_axis_robot_dict.items():
        existing_data = models.MultiAxisDataPoint.objects.filter(tag_name=key,	timestamp=updated_timestamp,	)
        if existing_data.exists():
            print("Data point already exists in DB")
        else:
            TempDataPoint = models.MultiAxisDataPoint(  tag_name=key,  tag_value=value, timestamp=updated_timestamp,  )
            TempDataPoint.save()

def read_json_file(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

