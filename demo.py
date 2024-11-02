import os
import numpy as np
import json
import cv2
from scrfd import SCRFD
from arcface_onnx import ArcFaceONNX
import uuid
import sqlite3
from datetime import datetime , timedelta
import random
import time

det_model = "/home/airi/Mylove/id/demo/models/det_500m.onnx"
rec_model = "/home/airi/Mylove/id/demo/models/w600k_mbf.onnx"
eye_classifier = cv2.CascadeClassifier('/home/airi/Mylove/id/demo/models/haarcascade_eye.xml')

#path = "rtsp://admin:jetsonnano1@10.10.0.126:75/h265/ch1/main/av_stream"
path = os.getenv('RTSP_STREAM_URL')
path = "/home/airi/Mylove/id/enter.mp4"

detector = SCRFD(det_model)
detector.prepare(1)

rec = ArcFaceONNX(rec_model)
rec.prepare(1)


data = json.load(open('/home/airi/Mylove/id/demo/data.json'))

conn = sqlite3.connect('/home/airi/Mylove/id/demo/database.db')
cursor = conn.cursor()

cap = cv2.VideoCapture(path)

start_time = datetime.now().replace(hour=4, minute=0, second=30, microsecond=0)
daily_time = datetime.now().replace(hour=4, minute=0, second=30, microsecond=0) + timedelta(days=1)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    current_time = datetime.now().replace(microsecond=0)
    
    faces, kpss = detector.autodetect(frame, max_num=20)
    for face, kps in zip(faces, kpss):

        x_min, y_min, x_max, y_max, confidence = int(face[0]), int(face[1]), int(face[2]), int(face[3]) ,face[4]
        if x_min < 0 or y_min < 0 or x_max < 0 or y_max < 0:
            continue
            

        odam = frame[y_min:y_max, x_min:x_max]   

        ###### check eyes #####
        if isinstance(eye_classifier.detectMultiScale(odam) , tuple):
            continue
        
        feat = rec.get(frame, kps)
        
        maxi = -1
        ID = 'person' + str(uuid.uuid4())
        
        for i in data:
            for db_id , db_feat in i.items():
                similarity = rec.compute_sim(feat, np.array(db_feat))
                if similarity > maxi:
                    maxi = similarity
                    ID = db_id  
                    
        if 0.2 <= maxi < 0.4:
            continue
        elif maxi < 0.2:
            ID = 'person' + str(uuid.uuid4())
            data.append({ID:feat})
        
        random_filename = f"/home/airi/Mylove/id/demo/images/{str(uuid.uuid4())}.jpg"
        
        
#         if datetime.strptime('00:00', '%H:%M').time() < current_time.time() < datetime.strptime('04:00', '%H:%M').time():
#             start_time -= timedelta(days=1)
        try:
            cursor.execute("SELECT departure_time FROM users WHERE name = ? ORDER BY departure_time DESC LIMIT 1" , (ID , ))
            last_seen = cursor.fetchone()[0]
        except: 
            last_seen = current_time.strftime('%Y-%m-%d %H:%M:%S')     
        
        cursor.execute("UPDATE users SET departure_time = ? WHERE name = ? AND arrival_time >= ?", (current_time.strftime('%Y-%m-%d %H:%M:%S'), ID, daily_time - timedelta(days=1)))
        check = True
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO users (name, arrival_time, departure_time, count, times, image) VALUES (?, ?, ?, ?, ?, ?)", (ID, current_time.strftime('%Y-%m-%d %H:%M:%S'), current_time.strftime('%Y-%m-%d %H:%M:%S'), 1, current_time.strftime('%Y-%m-%d %H:%M:%S'), random_filename))   
                                                                                                                                                                                            
            check = False
            cv2.imwrite(random_filename, odam)
            
        time_diff = datetime.now().replace(microsecond=0) - datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S")
        try:
            if check and time_diff > timedelta(minutes=1):
                
                ### update times list ###
                cursor.execute("SELECT times FROM users WHERE name = ?", (ID,))
                times = cursor.fetchone()
                times = times[0]
                updated_times = f"{times},{current_time}"
                cursor.execute("UPDATE users SET times = ? WHERE name = ?", (updated_times, ID))
                
                ###  count increase ###
                cursor.execute("UPDATE users SET count = count + 1 WHERE name=?", (ID,))
        except:pass
        
    
        if daily_time == current_time.strftime('%Y-%m-%d %H:%M:%S'):
            three_days_ago = datetime.now() - timedelta(days=3)
            three_days_ago_str = three_days_ago.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("SELECT image FROM users WHERE arrival_time < ?", (three_days_ago_str,))

            image_paths = cursor.fetchall()

            # Delete the image files
            try:
                for image_path in image_paths:
                    if image_path[0] and os.path.exists(image_path[0]):
                        os.remove(image_path[0])
            except:pass

            # Delete the rows from the database
            cursor.execute("DELETE FROM users WHERE arrival_time < ?", (three_days_ago_str,))
            
            ### clean data.json ###
            commands = []
            for i in data:
                for db_id , db_feat in i.items():
                    if not db_id.startswith('person'):
                        commands.append({db_id:db_feat})
            data = commands
            with open("data.json", "w") as outfile: 
                json.dump(data, outfile)
            
            daily_time += timedelta(days=1) 
            
            time.sleep(1)
            
    conn.commit()

cap.release()
cv2.destroyAllWindows()
conn.close()
        
