from PIL import Image, ImageDraw
import numpy
import cv2


COLOR_MAP = {
    '0': (0, 0, 255),
    '1': (255, 0, 0),
    'C': (128, 0, 0),
    'D': (0, 0, 128)}

def get_cd_matrix(filename, W, H):
    with open(filename) as f:
        data_str = f.read().replace('\t', '').split('\n')
        matrix = list(numpy.array(data_str).reshape((-1, W, H)))
    return matrix


##def get_color_sum(m, psize, x, y):
##    n = sum(list(map(lambda x: int(x), list(m[int(x/psize)][int(y/psize)]))))
##    return 64*n, 0, 64*(4-n)


def get_color_triangle(m, psize, x, y):
    w = int(x / psize)
    h = int(y / psize)
    x %= psize
    y %= psize
    if x == 0 or y == 0:
        return 0, 0, 0
    if x < y:
        n = 0 if x+y < psize else 3
    else:
        n = 1 if x+y < psize else 2
    return COLOR_MAP[m[w][h][n]]


def main():
    saveImage = False
    W = 7
    H = 7
    psize = 41
    name = 'edge1'
    width = W * psize
    height = H * psize
    iml = []
    matrix_data = get_cd_matrix(name + '.txt', W, H)
    for i, m in enumerate(matrix_data):
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for x in range(width):
            for y in range(height):
                draw.point((x, y), fill=get_color_sum(m, psize, x, y))
        iml.append(image)
        if saveImage: image.save('images/{}_{:02d}.jpg'.format(name, i+1), 'jpeg')
    iml[0].save('images/'+name+'.gif',
                save_all=True,
                append_images=iml,
                duration=1000)


if __name__ == '__main__':
    main()

