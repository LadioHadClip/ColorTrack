import os
import collections as ds

import cv2

import bitmap


# Data Structure for initial objects

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


# Opencv GUI


def main():
    objSlots = ObjectSlots(10)
    try:
        breaks = [(5, 4), (5, 2), (11, 5)]
        cur = breaks.pop(0)
        for i in range(20):
            print('==== {} ===='.format(i))
            idx = objSlots.next_slot()
            if idx == -1:
                break
            A = InitializedObject(id=idx, x1=0, y1=0, x2=100, y2=100)
            objSlots.set_slot(A, A.id)
            print('nEXT: {}'.format(objSlots.next_slot()))
            while i == cur[0]:
                objSlots.clear_slot(cur[1])
                print('Clear {}'.format(cur[1]))
                print('nEXT: {}*'.format(objSlots.next_slot()))
                if len(breaks) > 0: 
                    cur = breaks.pop(0)
                else:
                    cur = (-1, 0)
    except Exception as e:
        print(e)
    finally:
        pass   

if __name__ == '__main__':
    main()