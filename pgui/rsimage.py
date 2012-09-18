""" resizable image """
import  pygame as pg
import os
from uiconsts import RES_DIR

class RSImage:
    pg.display.init()

    _cache = {}
    CACHE_SIZE = 20

    @staticmethod
    def load(filename):
        cache = RSImage._cache
        if filename in cache:
            cnt, image = cache[filename]
            cache[filename] = (cnt + 1, image)
            return image
        if len(RSImage._cache) >= RSImage.CACHE_SIZE:
            minUse = -1
            for f, (image, cnt) in cache.iteritems():
                if minUse == -1 or cnt < minUse:
                    minUse = cnt
            for f, (image, cnt) in cache.iteritems():
                if cnt == minUse:
                    break
            del cache[f]
        try:
            image = pg.image.load(filename).convert_alpha()
        except pg.error:
            image = pg.image.load(os.path.join(RES_DIR, filename)).convert_alpha()
        cache[filename] = (1, image)
        return image

    def __init__(self, filename, mw, mh):
        """
        filename: the image filename;
        mw: margin width;
        mh: margin height.
        """
        image = self.load(filename)
        self.subImages = self.split(image, mw, mh)
        self.mw, self.mh = mw, mh
        w, h = image.get_size()
        if w < mw * 2:
            self.mw = w / 2
        if h < mh * 2:
            self.mh = h / 2

    def split(self, image, mw, mh):
        subImages = {}
        w, h = image.get_size()
        w1 = w - mw * 2
        h1 = h - mh * 2
        def sub(i, j, x, y, w, h):
            subImages[i, j] = image.subsurface(pg.Rect((x, y), (w, h)))
        sub(0, 0, 0, 0, mw, mh)
        sub(0, 1, mw, 0, w1, mh)
        sub(0, 2, mw + w1, 0, mw, mh)

        sub(1, 0, 0, mh, mw, h1)
        sub(1, 1, mw, mh, w1, h1)
        sub(1, 2, mw + w1, mh, mh, h1)

        sub(2, 0, 0, mw + h1, mw, mh)
        sub(2, 1, mw, mw + h1, w1, mh)
        sub(2, 2, mw + w1, mw + h1, mw, mh)
        return subImages

    def generate(self, size):
        mw, mh = self.mw, self.mh
        w, h = size
        w1 = w - mw * 2
        h1 = h - mh * 2
        if w1 < 0:
            mw = w / 2
            w1 = 0
        if h1 < 0:
            mh = h / 2
            h1 = 0
        image = pg.Surface((w, h)).convert_alpha()
        image.fill((0, 0, 0, 0))
        def blit(i, j, x, y, w, h):
            image.blit(pg.transform.smoothscale(self.subImages[i, j], (int(w), int(h))), (x, y))

        blit(0, 0, 0, 0, mw, mh)
        blit(0, 1, mw, 0, w1, mh)
        blit(0, 2, mw + w1, 0, mw, mh)

        blit(1, 0, 0, mh, mw, h1)
        blit(1, 1, mw, mh, w1, h1)
        blit(1, 2, mw + w1, mh, mh, h1)

        blit(2, 0, 0, mw + h1, mw, mh)
        blit(2, 1, mw, mw + h1, w1, mh)
        blit(2, 2, mw + w1, mw + h1, mw, mh)

        return image

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    mw, mh = map(int, sys.argv[2:4])
    screen = pg.display.set_mode((1, 1), 0, 32)
    pg.display.iconify()
    rsi = RSImage(filename, mw, mh)
    image = rsi.generate((200, 100))
    pg.image.save(image, 'rsi.png')
