import os
import cv2

CAP_PROPS_ID = {
    'fps': cv2.CAP_PROP_FPS,
    'start_frame': cv2.CAP_PROP_POS_FRAMES,
    'nframe': cv2.CAP_PROP_FRAME_COUNT,
    'height': cv2.CAP_PROP_FRAME_HEIGHT,
    'width': cv2.CAP_PROP_FRAME_WIDTH,
    'fourcc': cv2.CAP_PROP_FOURCC,
}

class VideoLoader(object):

    def __init__(self, path):
        self.base_path = path
        self.cap = cv2.VideoCapture(self.base_path)

    def get(self, start=-1, count=16):
        if start != -1:
            self.cap.set(CAP_PROPS_ID['start_frame'], start)
        
        flag = True
        res = []
        cnt = count
        while flag:
            _, frame = self.cap.read()
            if _:
                res.append(frame)
                cnt = cnt - 1
                if cnt == 0:
                    yield res, count - cnt
                    cnt = count
                    res = []
            else:
                yield res, count - cnt
                cnt = count
                res = []
                flag = False

    def info(self, key='all'):
        if key == 'all':
            return {
               _k:self.cap.get(CAP_PROPS_ID[_k]) for _k in CAP_PROPS_ID 
            } 
        else:
            return self.cap.get(CAP_PROPS_ID[key])

    def reset(self):
        self.cap.set(CAP_PROPS_ID['start_frame'], 0)


def main():
    path = 'F:\\data\\animal\\nmice_color\\ch01_20180601183430.mp4'
    loader = VideoLoader(path)
    total = 0
    for frames, nframe in loader.get():
        print(nframe, total)
        total = nframe + total
        for frame in frames:
            cv2.imshow('current frame', frame)
            cv2.waitKey(1)
        

if __name__ == '__main__':
    main()
