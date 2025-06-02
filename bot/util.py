import multiset
from model import m

def MS(data):
    return multiset.Multiset(data)

def getChildren(runs,tilesAvailable):
    children = []
    runs_list = list(runs)

    if tilesAvailable == 2:
        children.append(MS( list(map(lambda a: min(a+1, 3), runs_list)) ))

    if tilesAvailable >= 1:
        for i in range(m):
            v = runs_list[i]

            # If other run is unfinished, cannot only add one tile and make it valid
            if 0 < runs_list[(i+1)%m] < 3:
                continue

            ms = MS([min((v+1), 3), 0])
            if ms not in children:
                children.append(ms)



    if runs == MS([0,0]) or runs == MS([0,3]) or runs == MS([3,3]):
        children.append(MS([0,0]))

    # print(f'RUNS -> {runs} tilesAvailable {tilesAvailable}\nChildren\n{children}')

    return children
