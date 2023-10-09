f = open('E:\myfiles\python\Linear_Memo\\test.nmf','r',encoding='UTF-8')
t = f.read()
l = t.split('\n')
o = ''
for i in range(len(l)):
    for j in range(i+1, len(l)):
        try:
            if l[i].split('<br />')[0] == l[j].split('<br />')[0]:
                l.remove(l[j])
        except:
            pass

for i in l:
    o += i + '\n'

f = open('E:\myfiles\python\Linear_Memo\\test.nmf','w',encoding='UTF-8')
f.write(o[:-1])