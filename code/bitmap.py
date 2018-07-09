class Bitmap(object):

    def __init__(self, num):
        assert num > 0, 'Bitmap: Initial number of bits not valid.'
        self._size = (num - 1) // 31 + 1
        self._array = [0] * self._size

    def _index(self, pos):
        btidx = pos // 31
        assert btidx < self._size, 'Bitmap: Position not valid.'
        ibtidx = pos % 31
        return btidx, ibtidx

    def set_1(self, pos):
        btidx, ibtidx = self._index(pos)
        bt = self._array[btidx]
        self._array[btidx] = bt | (1 << ibtidx)
        print(self._array)

    def set_0(self, pos):
        btidx, ibtidx = self._index(pos)
        bt = self._array[btidx]
        self._array[btidx] = bt & ~(1 << ibtidx)
    
    def check(self, pos):
        btidx, ibtidx = self._index(pos)
        bt = self._array[btidx]
        return not (bt & (1 << ibtidx) == 0)


def main():
    b = Bitmap(31)
    b = Bitmap(32)
    b.set_1(12)
    b.set_1(32)
    b.set_1(0)
    print(b.check(32), b.check(12), b.check(0))
    b.set_0(12)
    print(b.check(32), b.check(12), b.check(0))

if __name__ == '__main__':
    main()