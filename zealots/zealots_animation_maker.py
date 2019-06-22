from PIL import Image, ImageDraw, ImageFont        # pip install pillow
import numpy
import cv2
import sys, os

FONT_MARGIN = 2
COLOR_MAP = {
    '1': (255, 35, 11),
    '0': (16, 194, 20),
    'C': (136, 0, 21),
    'D': (7, 92, 10)}
OUTPATH = 'output'

def get_attr(info, default=None, isBoolean=False):
    value = input(info + ('' if default is None \
                  else '(default: {})'.format(default)) + ': ').strip()
    if value == '' and default is not None: value = default
    if isBoolean: value = True if value[0] in 'yY' else False
    return value

def get_cd_matrix(datafile, layoutfile, W, H):
    with open(layoutfile) as f:
        layout_str = f.read().replace('\n', '').replace('\t', '')
    with open(datafile) as f:
        player_str = f.read().replace('C', '1').replace('D', '0').split('\n')
    data_str = ''
    n_players = layout_str.count('_')
    cnt = 0
    if len(player_str) % n_players != 0:
        print('It seems that you have choosen a wrong layout file, please check it.')
        exit(1)
    for i in range(int(len(player_str)/layout_str.count('_'))):
        for p in layout_str:
            if p == '_':
                data_str += player_str[cnt]
                cnt += 1
            else:
                data_str += p
    matrix = list(numpy.array(list(data_str)).reshape((-1, W, H)))
    for i in range(len(matrix)):
        matrix[i] = matrix[i].T
    return matrix

def get_image_list(matrix_data, width, height, psize, title_height):
    length = len(matrix_data)
    print('Generate rounds images (0/{})...'.format(length), end='')
    if title_height:
        fontsize = 1
        font = ImageFont.truetype("arial.ttf", fontsize)
        while font.getsize('Round: 999')[1] < title_height - FONT_MARGIN * 2:
            fontsize += 1
            font = ImageFont.truetype("arial.ttf", fontsize)
    iml = []
    for i, m in enumerate(matrix_data):
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for x in range(width):
            for y in range(height - title_height):
                draw.point((x, y), fill=get_color(m, psize, x, y))
        if title_height > 0:
            print('\rGenerate rounds images ({}/{})...'\
                  .format(i+1, length), end='')
            draw.text((10, height-title_height + FONT_MARGIN), 'Round: ' + str(i+1),
                  font=font, fill='#000000')
        iml.append(image)
    print('Done')
    return iml

def get_color(m, psize, x, y):
    return COLOR_MAP[m[int(x/psize)][int(y/psize)]]

def save_iml(name, iml):
    if not os.path.exists(OUTPATH+'/'+name):
        os.makedirs(OUTPATH+'/'+name)
    print('Saving Images (0/{})...'.format(len(iml)), end='')
    for i, image in enumerate(iml):
        print('\rSaving Images ({}/{})...'.format(i+1, len(iml)), end='')
        image.save('{}/{}/{:02d}.jpg'.format(OUTPATH, name, i+1), 'jpeg')
    print('Done')
        
def save_gif(name, iml, duration):
    print('Saving GIF...', end='')
    iml[0].save(OUTPATH+'/'+name+'.gif', save_all=True, append_images=iml,
                duration=duration)
    print('Done')
    
def save_video(name, iml, width, height, fps=24, vtype='mp4'):
    if vtype.lower() not in ['mp4', 'avi']:
        print('Error video type.')
        return None
    print('Saving {} (0/{})...'.format(vtype, len(iml)), end='')
    codecs = {
        'mp4': cv2.VideoWriter_fourcc(*'MP4V'),
        'avi': cv2.VideoWriter_fourcc(*'XVID'),
        }
    video = cv2.VideoWriter(OUTPATH+'/' + name + '.' + vtype,
                            codecs[vtype], float(fps),
                            (width,height), isColor=False)
    for i, im in enumerate(iml):
        print('\rSaving {} ({}/{})...'.format(vtype, i+1, len(iml)), end='')
        image = cv2.cvtColor(numpy.array(im), cv2.COLOR_RGB2BGR)
        for i in range(int(fps)):
            video.write(image)
    cv2.destroyAllWindows()
    video.release()
    print('Done')

def process():
    name = get_attr('Data file (without ".txt")')
    layout = get_attr('Layout file (without ".txt")')
    W = int(get_attr('Grid width'))
    H = int(get_attr('Grid height'))
    psize = int(get_attr('Pixels per person', 40))
    title_height = int(get_attr('Height of title for round (0 for no title)', 0))
    isSaveImage = get_attr('Save Images (y/n)', 'n', True)
    isSaveGif = get_attr('Save GIF (y/n)', 'n', True)
    isSaveAvi = get_attr('Save Avi (y/n)', 'n', True)
    isSaveMp4 = get_attr('Save Mp4 (y/n)', 'y', True)
    if not isSaveImage and not isSaveGif and not isSaveAvi and not isSaveMp4:
        return None

    width = W * psize
    height = H * psize + title_height
    
    print('[Processing:', name+'.txt]')
    matrix_data = get_cd_matrix(name + '.txt', layout+'.txt', W, H)
    iml = get_image_list(matrix_data, width, height, psize, title_height)
    if isSaveImage: save_iml(name, iml)
    if isSaveGif: save_gif(name, iml, 1000)
    if isSaveAvi: save_video(name, iml, width, height, vtype='avi')
    if isSaveMp4: save_video(name, iml, width, height, vtype='mp4')
    
def process_sequence(fname):
    with open(fname) as f:
        f.readline()
        lines = f.read().strip().split('\n')
        for line in lines:
            data = line.split(',')
            name = data[0]
            layout = data[1]
            W = int(data[2])
            H = int(data[3])
            psize = int(data[4])
            title_height = int(data[5])
            isSaveImage = True if data[6][0] in 'yY' else False
            isSaveGif = True if data[7][0] in 'yY' else False
            isSaveAvi = True if data[8][0] in 'yY' else False
            isSaveMp4 = True if data[9][0] in 'yY' else False
            if not isSaveImage and not isSaveGif and \
               not isSaveAvi and not isSaveMp4: continue
            width = W * psize
            height = H * psize + title_height
            print('[Processing:', name+'.txt]')
            matrix_data = get_cd_matrix(name + '.txt', layout+'.txt', W, H)
            iml = get_image_list(matrix_data, width, height, psize, title_height)
            if isSaveImage: save_iml(name, iml)
            if isSaveGif: save_gif(name, iml, 1000)
            if isSaveAvi: save_video(name, iml, width, height, vtype='avi')
            if isSaveMp4: save_video(name, iml, width, height, vtype='mp4')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        process_sequence(sys.argv[1])
    else:
        process()
