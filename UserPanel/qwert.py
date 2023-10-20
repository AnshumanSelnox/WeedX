list=[[5,10,4],[25,8,10],[10,9,1],[6,7,65]]

def FirstAsc(i):
    return i[0]
list.sort(key=FirstAsc)
print(list)


def SecondAsc(i):
    return i[1]
list.sort(key=SecondAsc)
print(list)


def ThirdAsc(i):
    return i[2]

list.sort(key=ThirdAsc)
print(list)
