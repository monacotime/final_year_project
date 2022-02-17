from flask import Flask, render_template, Response, request
import numpy as np
import cv2
import json

# 0 -> Original video
# 1 -> Video with Object Detection
# 2 -> Video with MaskRCNN
# 3 -> Video with Patchmatch

vid_paths = [r"C:\Users\monac\work\final_year_project\videos\0", r"C:\Users\monac\work\final_year_project\videos\1"]

class Controller:
    def __init__(self, paths) -> None:
        self.selected_scene, self.selected_cache = 0, 1
        # for each scene in a scene path
        self.all_scenes = []
        for path in paths:
            scene = []
            # for each cache in a scene
            for i in range(4):
                # read all cache
                cache = self.pack_frames(path+"\\"+str(i)+".mp4")
                scene.append(cache)
            # save it all in scenes
            self.all_scenes.append(scene)
        pass

    def pack_frames(self, path):
        reader = cv2.VideoCapture(path)
        cache = []
        while True:
            success, frame = reader.read()
            if not success:
                break
            else:
                cache.append(frame)
        reader.release()
        return cache

    def gen_frames(self):
        counter = 0
        while True:
            
            scene = self.all_scenes[self.selected_scene]
            cache = scene[self.selected_cache]
            origi = scene[0]

            # permanently loop the videos
            if counter == len(cache)-1:
                counter = 0
            counter += 1
            
            # print("status ->", counter, len(cache)) # debug
            
            origi_frame = origi[counter]
            cache_frame = cache[counter]
            
            side_by_side_frame = np.concatenate((origi_frame, cache_frame), axis=1)
            yield self.package_frame(side_by_side_frame)

    def package_frame(self, frame):
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        return (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


app = Flask(__name__)
controller = Controller(vid_paths)

@app.route('/')
def index():
    return render_template('demo.html', content="Hello World!")

@app.route('/video_feed')
def video_feed():
    return Response(controller.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/config', methods=["POST"])
def config():
    data = json.loads(request.data.decode("utf-8"))
    print(data, data["scene"], data["cache"], type(data["scene"]), type(data["cache"]))
    controller.selected_scene = data["scene"]
    controller.selected_cache = data["cache"]
    return "Config Changed Successfully"



if __name__ == "__main__":
    app.run(debug=True)