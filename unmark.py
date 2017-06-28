import sys
import os
import glob
from PIL import Image

_pattern_file_path = os.path.abspath('_empty_512.png')


def get_data(height, width, interval, datalen, start):
    # first line: 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0 ...
    data = []
    raw_line = [0] * interval
    raw_line.extend([1] * datalen)
    packlen = interval + datalen
    raw = raw_line * (int(width / packlen) + 2)
    start = packlen - start
    for i in range(height):
        if start > packlen:
            start = (start % packlen)
        data.extend(raw[start:start + width])
        start += 1
    return data


def get512():
    return get_data(512, 512, 13, 7, 3)


def get256():
    return get_data(256, 256, 13, 7, 3)


def get128():
    return get_data(128, 128, 13, 7, 3)


def get48():
    return get_data(48, 48, 5, 5, 2)


raw_data = {
    # 48: get48,
    128: get128,
    256: get256,
    512: get512
}


def transparent(point):
    if point[3] != 255 and (66 < point[0] < 70) and (66 < point[1] < 70) \
            and (62 < point[2] < 66):
        return True
    return False


def rec(x, i):
    a, b, c, d = x
    a = int((a - 68 * i) / (1 - i))
    b = int((b - 68 * i) / (1 - i))
    c = int((c - 64 * i) / (1 - i))
    return (a, b, c, d)


def unmark(filename):
    image = Image.open(filename)
    image = image.convert("RGBA")
    image = unmark_process(image)
    save_file(filename, image)


def unmark_process(image):
    kk = image.load()
    func = raw_data.get(image.size[0])
    print("SIZE: ", image.size)
    if not func:
        print("NOT SUPPORT SIZE, USE ALTERNALTIVE WAY")
        resized_img = resize_file_to_512(image)
        processd_img = unmark_process(resized_img)
        restored_size_img = restore_file_to_origin(processd_img, image)
        return restored_size_img

    nodes = func()

    for index, node in enumerate(nodes):
        if node == 0:
            continue

        i = index % image.size[1]
        j = index / image.size[1]

        if transparent(kk[i, j]):
            kk[i, j] = (0, 0, 0, 0)
        else:
            if (i > 1 and nodes[index - 1] == 0) or (j < image.size[1] - 1 and nodes[index + 1] == 0):
                kk[i, j] = rec(kk[i, j], 0.015)
            elif (i > 2 and nodes[index - 2] == 0) or (j < image.size[1] - 2 and nodes[index + 2] == 0):
                kk[i, j] = rec(kk[i, j], 0.065)
            else:
                kk[i, j] = rec(kk[i, j], 0.073)
    return image


def resize_file_to_512(img):
    pattern = Image.open(_pattern_file_path)
    pattern.paste(img.crop((0, 0) + img.size))
    return pattern


def restore_file_to_origin(resized_img, origin_img):
    return resized_img.crop((0, 0) + origin_img.size)


def save_file(filename, im):
    new_name = filename.lower().replace(".png", ".new.png")
    print("NEW: ", new_name)
    im.save(new_name, "PNG")


def show(x, n):
    for i in range(n):
        for j in range(n):
            print(x[i * n + j]),
        print()


if __name__ == '__main__':
    sPath = os.path.abspath(sys.argv[1])
    if os.path.isdir(sPath):
        for filepath in glob.glob(os.path.join(sPath, '*.png')):
            if not filepath.endswith('.new.png'):
                unmark(filepath)
    else:
        unmark(sPath)
