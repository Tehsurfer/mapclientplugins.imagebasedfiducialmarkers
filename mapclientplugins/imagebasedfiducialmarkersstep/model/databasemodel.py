# Databasemodel.py is used to manage human generated data

import json
import requests

class CloudDataBase(object):
    def __init__(self, videoName):
        self.data_dict = {}
        self.video_name = videoName
        self.database_locations = {'P1760 IVC Occ_Trim.mp4': 'https://jsonstorage.net/api/items/40bc8559-51a0-45ea-a93d-c16264011992',
                                   'P1760 IVC Occ.MOV': 'https://jsonstorage.net/api/items/0dd64617-0d18-49c8-bd94-3f9e26eb4c0a',
                                    'P1760 LCVN 2x THR.MOV': 'https://jsonstorage.net/api/items/6b229986-b0ad-4d4c-bc5b-55865d367092',
                                   'P1760 LCVN THR.MOV':'https://jsonstorage.net/api/items/b53a584d-cfbc-436e-a3ff-6a156af8055f',
                                    'P1760 RST THR.MOV':'https://jsonstorage.net/api/items/62c10113-3eab-4618-95e5-fceec211f0a5',
                                   }
        self.data_dict = self.retrieve_database()

    def load_json(self, filename):
        with open(filename, 'r') as fp:
            return json.load(fp)

    def retrieve_database(self):
        url = self.database_locations[self.video_name]
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f'Error! Could not connect to the database: {url} /'
                  f' Error was: {resp.json()}')


    def get_data_at_frame(self, frame_id):
        try:
            return self.data_dict['AnnotatedFrames'][str(frame_id)]
        except KeyError:
            return False

    def upload_additions_to_database(self, frame_additions, modify=False):

        cloud_dict = self.retrieve_database()

        for frame_addition in frame_additions:
            frame_key = list(frame_addition.keys())[0]
            if frame_key not in cloud_dict['AnnotatedFrames']:
                cloud_dict['AnnotatedFrames'][frame_key] = frame_addition[frame_key]
            elif modify:
                cloud_dict['AnnotatedFrames'][frame_key] = frame_addition[frame_key]

        headers = {'Content-Type': "application/json; charset=utf-8",'dataType': "json"}
        data = json.dumps(cloud_dict)
        url = self.database_locations[self.video_name]
        resp = requests.put(url, headers=headers, data=data)
        if resp.status_code == 200 or 201:
            print(f'Data successfull uploaded: {resp.json()})')
        else:
            print(f'Error! Could not upload to the database: {resp.json()}')

        self.data_dict = cloud_dict