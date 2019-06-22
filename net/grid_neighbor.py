def get_neighbor_array(h, w):
    neighbor = []
    for i in range(h):
        for j in range(w):
            # x = i * w + j
            neighbor.append({
                'left': i * w + (j + w - 1) % w,
                'up': (i + h - 1) % h * w + j,
                'right': i * w + (j + 1) % w,
                'down': (i + 1) % h * w + j
            })
    return neighbor

if __name__=='__main__':
    w = int(input('网络的宽：'))
    h = int(input('网络的高：'))
    nei = get_neighbor_array(h, w)
    with open('neighbors.csv', 'w') as f:
        f.write('id,left,up,right,down\n')
        for i, n in enumerate(nei):
            f.write('{},{},{},{},{}\n'.format(i+1, n['left']+1,
                                n['up']+1, n['right']+1, n['down']+1))
