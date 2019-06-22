try:
    from otree.api import BasePlayer, BaseSubsession
except:
    raise Exception('You should put this library into an oTree app folder with models.py.')

try:
    from settings import NET_PATH
except:
    print('Set your oTree net save path in settings.py with "NET_PATH" variable.')
    NET_PATH = '/home/taoge/www/otree_net/'

from random import random, randint

# Net generation part

class OtreeNet:
    def __init__(self, subsession):
        if not isinstance(subsession, BaseSubsession):
            raise ValueError('Class should be Subsession.')
        self._players = subsession.get_players()
        self._links = {}
    
    def __str__(self):
        nm = self.neighborsMatrix()
        s = ""
        for i in range(0, len(nm)):
            s += str(i+1) + ": " + str(nm[i]) + "\n"
        return s
    
    def _getPair(self, p1, p2):
        if isinstance(p1, BasePlayer) and isinstance(p2, BasePlayer):
            p1, p2 = p1.id_in_subsession, p2.id_in_subsession
        if isinstance(p1, int) and isinstance(p2, int):
            if p1 < 1 or p1 > len(self._players) or \
               p2 < 1 or p2 > len(self._players):
                raise ValueError('ID out of range.')
            if p1 == p2: raise ValueError('Should link two different point.')
            if p1 > p2: p1, p2 = p2, p1
            return (p1, p2)
        raise ValueError('Parameters should be int or Player object.')
    
    def totalNodesNum(self):
        return len(self._players)
    
    def totalLinksNum(self):
        return len(self._links)
    
    def totalDegree(self):
        return self.totalLinksNum()*2
    
    def averageDegree(self):
        return self.totalDegree()/self.totalNodesNum()
    
    def isLinked(self, p1, p2):
        pair = self._getPair(p1, p2)
        return pair in self._links
    
    def neighbors(self, p):
        if isinstance(p, BasePlayer):
            p = p.id_in_subsession
        if p < 1 or p > len(self._players):
            raise ValueError('ID out of range.')
        nei = []
        for l in self._links.keys():
            if p in l: nei.append(l[1] if l[0] == p else l[0])
        return nei
    
    def neighborsMatrix(self):
        m = []
        for p in self._players:
            m.append(self.neighbors(p))
        return m
    
    def removeLink(self, p1, p2):
        pair = self._getPair(p1, p2)
        if pair in self._links:
            del self._links[pair]
        
    def addLink(self, p1, p2, weight=1):
        if weight == 0: self.removeLink(p1, p2)
        pair = self._getPair(p1, p2)
        self._links[pair] = weight
    
    def getAllLinks(self):
        return self._links.copy()
    
    def save(self, net_name):
        self.saveLinks(net_name+'_links.csv')
        self.saveNeighbors(net_name+'_neighbors.csv')
        
    def saveLinks(self, file_name):
        with open(NET_PATH+file_name, 'w') as f:
            for i, j in self._links.keys():
                f.write('{},{},{}\n'.format(i, j, self._links[(i, j)]))
    
    def saveNeighbors(self, file_name):
        m = self.neighborsMatrix()
        max_len = max([len(i) for i in m])
        with open(NET_PATH+file_name, 'w') as f:
            f.write('PlayerID,Neighbors'+','*(max_len-1)+'\n')
            for i, line in enumerate(m):
                f.write('{},{}{}\n'.format(i+1, 
                              ','.join(list(map(str, line))),
                              ','*(max_len-len(line))))


class OtreeFullConnectedNet(OtreeNet):
    def __init__(self, subsession):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                self.addLink(i, j)
        
        
class OtreeRegularNet(OtreeNet):
    def __init__(self, subsession, links_num=2):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        if links_num < 0 or links_num > n:
            raise ValueError('Illegal links value.')
        for i in range(0, n):
            for j in range(i+1, i+1+links_num):
                self.addLink(i+1, j%n + 1)
        self._links_num = links_num


class OtreeERRandomNet(OtreeNet):
    def __init__(self, subsession, link_prob=0.2):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        if link_prob < 0 or link_prob > 1:
            raise ValueError('Illegal link probability.')
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                if random() > link_prob: continue
                self.addLink(i, j)
        self._link_prob = link_prob


# This net may have some problems
class OtreeFakeERRandomNet(OtreeNet):
    def __init__(self, subsession, average_degree):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        if average_degree > n-1 or average_degree < 0:
            raise ValueError("Illegal average degree value.")
        if isinstance(average_degree, float):  # Float for inflating
            p = average_degree/n
            avg_degree = average_degree
            while self.averageDegree() < avg_degree:
                if random() < p:
                    self.addLink(randint(1, n), randint(1, n))
        elif isinstance(average_degree, int):  # Integer for reconnecting
            for i in range(0, n):
                for j in range(i + 1, i + 1 + int(average_degree/2)):
                    self.addLink(i+1, j%n + 1)
            total_change_links = int(n * average_degree/2)
            for i in range(1, n+1):
                for j in range(0, int(average_degree/2)):
                    while True:
                        newj = randint(1, n)
                        if newj != i and newj != (i+j)%n+1 \
                            and not self.isLinked(i, newj): break
                    self.removeLink(i, (i+j)%n+1);
                    self.addLink(i, newj);
        else:
            raise TypeError('Parameters recieves an integer or a float.')


class OtreeGridNet(OtreeNet):
    def __init__(self, subsession, width, height, neighbor_num=4):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        w, h = width, height
        if w < 0 or h < 0 or w * h != n:
            raise ValueError('Illegal width or height value.')
        if neighbor_num not in [4, 8]:
            raise ValueError('Neighbor num is not supported, should be 4 or 8.')
        for i in range(h):
            for j in range(w):
                if neighbor_num >= 4:
                    self.addLink(((i+h-1)%h)*w+j+1, i*w+j+1)
                    self.addLink(i*w+((j+w-1)%w)+1, i*w+j+1)
                if neighbor_num >= 8:
                    self.addLink(((i+h-1)%h)*w+(j+w-1)%w+1, i*w+j+1)
                    self.addLink(((i+1)%h)*w+(j+w-1)%w+1, i*w+j+1)
        self._gridw, self._gridh = w, h


class OtreeCubicNet(OtreeNet):
    def __init__(self, subsession, length, width, height):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        l, w, h = length, width, height
        if l < 0 or w < 0 or l < 0 or l * w * h != n:
            raise ValueError('Illegal length, width or height value.')
        for i in range(h):
            for j in range(l):
                for k in range(w):
                    self.addLink(((i+h-1)%h)*w*l+j*w+k+1, i*w*l+j*w+k+1)
                    self.addLink(i*w*l+((j+l-1)%l)*l+k+1, i*w*l+j*w+k+1)
                    self.addLink(i*w*l+j*w+((k+w-1)%w)+1, i*w*l+j*w+k+1)
        self._cubel, self._cubew, self._cubeh = l, w, h
            

class OtreeHoneycombNet(OtreeNet):
    def __init__(self, subsession, honeycomb_width, honeycomb_height):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        w, h = honeycomb_width, honeycomb_height
        if w < 0 or h < 0 or 2 * w * h != n:
            raise ValueError('Illegal honeycomb width or height value.')
        for i in range(h):
            for j in range(w):
                self.addLink(2*(i*w+j)+1, (2*(i*w+j)+2*w+1)%(2*w*h)+1)
                self.addLink(2*(i*w+j)+1, 2*i*w+((2*j+1)%(2*w))+1)
                self.addLink(2*i*w+((2*j+1)%(2*w))+1, 2*i*w+((2*j+2)%(2*w))+1)
        self._hcw = w
        self._hch = h


class OtreeKagomeNet(OtreeNet):
    def __init__(self, subsession, kagome_width, kagome_height):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        w, h = kagome_width, kagome_height
        if w < 0 or h < 0 or 3 * w * h != n:
            raise ValueError('Illegal kagome width or height value.')
        for i in range(h):
            for j in range(w):
                self.addLink(3*(i*w+j)+1, 3*(i*w+j)+2)
                self.addLink(3*(i*w+j)+1, 3*(i*w+j)+3)
                self.addLink(3*(i*w+j)+1, 3*(i*w+(j+1)%w)+2)
                self.addLink(3*(i*w+j)+1, 3*(((i*w+j)+w)%(h*w))+3)
                self.addLink(3*(i*w+j)+3, 3*(i*w+(j+1)%w)+2)
                self.addLink(3*(i*w+j)+2, 3*(((i*w+j)+w)%(h*w))+3)
        self._kgw, self._kgh = w, h


class OtreeScaleFreeNet(OtreeNet):
    def __init__(self, subsession, init_m0=3):
        OtreeNet.__init__(self, subsession)
        n = len(self._players)
        if init_m0 > n:
            raise ValueError('Illegal init_m0, should be less than ' + \
                             str(n) + '.')
        self._cn = init_m0 + 1    # Current node
        
    def addLink(self, p1, p2, weight=1):
        if p1 > self._cn - 1 or p2 > self._cn - 1:
            raise ValueError('Nodes should be no more than current node: ' + \
                            str(self._cn) + '.')
        OtreeNet.addLink(self, p1, p2)
    
    def fullConnectInitSFVex(self):
        if self.totalLinksNum() >= (self._cn-1)*(self._cn-2)/2:
            return None
        for i in range(1, self._cn-1):
            for j in range(i+1, self._cn):
                self.addLink(i, j)
        
    def fillSFVex_BAModel(self, links_per_node):
        vn = self.totalNodesNum()
        if self._cn > vn: return None                 # Already filled
        if links_per_node >= self._cn: return None    # m > m0   
        while self._cn <= vn:
            total = 2 * self.totalLinksNum()
            for i in range(links_per_node):
                t = total          # A copy of total
                for j in range(1, self._cn):
                    if self.isLinked(j, self._cn): continue
                    nv = len(self.neighbors(j))       # nv = self.degree(j)
                    t -= nv
                    if random() > nv/(t + nv): continue;
                    OtreeNet.addLink(self, j, self._cn)
                    total -= nv
                    break
            self._cn += 1

            
class OtreeWSSmallWorldNet(OtreeRegularNet):
    def __init__(self, subsession, links_num=2, relink_prob=0.5):
        OtreeRegularNet.__init__(self, subsession, links_num)
        n = len(self._players)
        if relink_prob < 0 or relink_prob > 1:
            raise ValueError('Illegal relink probability.')
        cnt = 0
        for link in self._links:
            if random() > relink_prob: continue
            if randint(0, 1): i, j = link
            else: j, i = link
            while True:
                newj = randint(1, len(self._players))
                if newj != j and newj != i: break
            cnt += 1
            self.removeLink(i, j)
            self.addLink(i, newj)
        print('Relink count:', cnt)
        self._links_num, self._relink_prob = links_num, relink_prob


class OtreeNWSmallWorldNet(OtreeRegularNet):
    def __init__(self, subsession, links_num=2, add_link_prob=0.05):
        OtreeRegularNet.__init__(self, subsession, links_num)
        n = len(self._players)
        if add_link_prob < 0 or add_link_prob > 1:
            raise ValueError('Illegal relink probability.')
        cnt = 0
        for i in range(1, n+1):
            for j in range(1, n+1):
                if i == j or random() > add_link_prob: continue
                cnt += 1
                self.addLink(i, j)
        print('Add links count:', cnt)
        self._links_num, self._add_link_prob = links_num, add_link_prob


# Deprecated nets
class OtreeFakeNet(OtreeNet):
    def __init__(self, subsession, *argv, **kargv):
        raise Exception('This type of net is deprecated.')
OtreeFakeERRandomNet = OtreeFakeNet


# Alias
OFull = OtreeFullConnectedNet
ORegular = OtreeRegularNet
OERRandom = OtreeERRandomNet
OGrid = OtreeGridNet
OCube = OtreeCubicNet
OHoneycomb = OtreeHoneycombNet
OKagome = OtreeKagomeNet
OScaleFree = OtreeScaleFreeNet
OWSSmall = OtreeWSSmallWorldNet
ONWSmall = OtreeNWSmallWorldNet
