import os
import collections as ds

import cv2
import json

import bitmap
import video_loader as vl


"""
    Data Structure for initial objects
"""

class InitializedObject(ds.namedtuple('INITObj', ['id', 'x1', 'y1', 'x2', 'y2'])):

    def __init__(self, **kwargs):
        assert self.x1 < self.x2 and self.y1 < self.y2, 'Object position is not valid.'
        self._chosen = False
        print('New Object #{}: ({},{}) -> ({},{})'.format(
            self.id, self.x1, self.y1, self.x2, self.y2
        ))

    def inBox(self, x, y):
        if x >= self.x1 and y >= self.y1 and x <= self.x2 and y <= self.y2:
            return True
        else:
            return False

    def chooseObject(self):
        self._chosen = True

    def releaseObject(self):
        self._chosen = False


class ObjectSlots(bitmap.Bitmap):

    def __init__(self, n_slot):
        super().__init__(num=n_slot)
        self._size = n_slot
        self._slots = [None] * n_slot
        self._first_empty = 0

    def next_slot(self):
        return self._first_empty

    def set_slot(self, obj, idx):
        assert idx < self._size and idx >= 0 and not self.check(idx), 'Slot #{} is not empty.'.format(idx)
        self._slots[idx] = obj
        self.set_1(idx)
        self._update(idx, -1) 

    def clear_slot(self, tidx):
        assert tidx < self._size and tidx >= 0 and self.check(tidx), 'Slot index not valid.'
        self._slots[tidx] = None
        self.set_0(tidx)
        if tidx < self._first_empty or self._first_empty == -1:
            self._update(tidx, 0)

    def find_slot(self, func, params, lru=False):
        for i in range(0, self._size) if not lru else range(self._size-1, -1, -1):
            if self.check(i):
                if func(self._slots[i], params):
                    return i, self._slots[i]
        return -1, None

    def get_slot(self, idx):
        assert idx < self._size and idx >= 0 and self.check(idx), 'Slot #{} is empty.'.format(idx)
        return self._slots[idx]

    def _update(self, idx, mode):
        if mode == -1:
            # SET
            for i in range(self._first_empty, self._size):
                if not self.check(i):
                    self._first_empty = i
                    break
            else:
                self._first_empty = -1
        else:
            # CLEAR
            self._first_empty = idx


"""
    Opencv GUI
"""

def localize(frame, name, old_size, new_size, max_slots=10):
    record_name = name + '_initial_objects.json'
    if os.path.exists(record_name):
        print('Initial objects have been localized. Now show the result.')
        print('  Remove the file if you want to re-localize.')
        print('  File path: ' + record_name)
        with open(record_name, 'r') as f:
            data = json.load(f)
            cur_frame = frame.copy()
            for _, obj in data['objects'].items():
                cv2.rectangle(
                    cur_frame,
                    (int(obj[0]), int(obj[1])),
                    (int(obj[2]), int(obj[3])),
                    (255, 0, 0),
                    2
                )
            cv2.imshow('Existed result', cur_frame)
            cv2.waitKey(0)
        return

    objSlots = ObjectSlots(max_slots)
    mode = 0    # 0-draw, 1-edit
    isDown = False
    isSelected = False
    cur_slot = -1
    cur_obj = [0, 0, 0, 0]   #[lx, ly, rx, ry]
    window = cv2.namedWindow('Choose object')

    def check(obj, params):
        return obj.inBox(params['x'], params['y'])

    def redrawGUI():
        # each slots, (255, 0, 0)
        # cur obj, (0, 255, 0)
        nonlocal frame, objSlots, max_slots, cur_obj, isSelected
        cur_frame = frame.copy()
        for i in range(0, max_slots):
            if objSlots.check(i):
                slot = objSlots.get_slot(i)
                cv2.rectangle(
                    cur_frame,
                    (int(slot.x1), int(slot.y1)),
                    (int(slot.x2), int(slot.y2)),
                    (255, 0, 0),
                    2
                )
        if any(cur_obj):
            _color = (0, 255, 0) if isSelected else (255, 0, 0)
            cv2.rectangle(
                cur_frame,
                (int(cur_obj[0]), int(cur_obj[1])),
                (int(cur_obj[2]), int(cur_obj[3])),
                _color,
                2
            )
        cv2.imshow('Choose object', cur_frame)

    def onMouse(event, x, y, flags, params):
        # callback
        # each press & release is a slot
        nonlocal isDown, objSlots, mode, isSelected, cur_slot, cur_obj
        if event == cv2.EVENT_LBUTTONDOWN:
            isDown = True
            if mode == 0:
                cur_slot = objSlots.next_slot()
                cur_obj[0] = x
                cur_obj[1] = y
            elif mode == 1:
                cur_slot, obj = objSlots.find_slot(check, {'x':x, 'y':y})
                if cur_slot == -1:
                    cur_slot = objSlots.next_slot()
                else:
                    isSelected = True
                    cur_obj = [obj.x1, obj.y1, obj.x2, obj.y2]
                    redrawGUI()
        elif event == cv2.EVENT_LBUTTONUP:
            isDown = False
            if mode == 0:
                objSlots.set_slot(
                    InitializedObject(
                        x1=cur_obj[0], y1=cur_obj[1],
                        x2=cur_obj[2], y2=cur_obj[3],
                        id=cur_slot),
                    cur_slot
                )
                cur_slot = objSlots.next_slot()
                cur_obj = [0, 0, 0, 0]
                redrawGUI()
        elif event == cv2.EVENT_MOUSEMOVE:
            if isDown and mode == 0:
                cur_obj[2] = x
                cur_obj[3] = y
                redrawGUI()
  
    # main part
    cv2.setMouseCallback('Choose object', onMouse)
    redrawGUI()
    inProcess = True
    while(inProcess):
        key = cv2.waitKey(0)
        print(key == ord('e'))
        # 'e'-edit, 'd'-delete, 's'-save, 'q'-exit
        if key & 0xFF == ord('e'):
            if not isDown:
                mode = 1 - mode
                isSelected = False
                cur_obj = [0, 0, 0, 0]
                print('Now mode={}'.format(mode))
        elif key & 0xFF == ord('d'):
            if mode == 1 and isSelected:
                isSelected = False
                objSlots.clear_slot(cur_slot)
                cur_obj = [0, 0, 0, 0]
                cur_slot = objSlots.next_slot()
                redrawGUI()
        elif key & 0xFF == ord('s'):
            # objslots -> file
            if not isDown:
                with open(record_name, 'w') as f:
                    record = {}
                    cnt = 0
                    # TODO: actual transform
                    record['objects'] = {}
                    for i in range(0, max_slots):
                        if objSlots.check(i):
                            slot = objSlots.get_slot(i)
                            record['objects'][str(i)] = [slot.x1, slot.y1, slot.x2, slot.y2]
                            cnt = cnt + 1
                    record['old_size'] = old_size
                    record['new_size'] = new_size
                    record['num_obj'] = cnt
                    json.dump(record, f)
                    print(record_name + 'Successfully saved')
        elif key & 0xFF == ord('q'):
            inProcess = False

"""
    Test
"""

def main():
    path = 'F:\\data\\animal\\nmice_color\\ch03_20180703185712'
    video_name = 'ch03_20180703185712_0cropped.avi'
    ext = '.avi'
    # new_tar = 1
    # new_ext = '.avi'
    # old_ext = '.mp4'
    new_size = (360, 640)

    loader = vl.VideoLoader(os.path.join(path, video_name))
    for frames, nframe in loader.get(count=16):
        frame = frames[0]
        old_size = frame.shape
        frame = cv2.resize(frame, new_size)
        localize(frame, os.path.join(path, video_name).replace(ext, ''), old_size, new_size)
        break
            
  

if __name__ == '__main__':
    main()