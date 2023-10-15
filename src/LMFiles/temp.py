f = open('E:\myfiles\python\Linear_Memo\src\LMFiles\\test.nmf','r',encoding='UTF-8')
t = f.read()
l = t.split('\n')
o = ''
for c in l:
    x = ''
    for n, p in enumerate(c.split('\t')):
        if n == 4 and float(p) > 1:
            x+=str(float(p)/100)+'\t'
        else:
            x+=p+'\t'
    l.remove(c)
    l.append(x)



for i in l:
    o += i + '\n'

f = open('E:\myfiles\python\Linear_Memo\src\LMFiles\\test1.nmf','w',encoding='UTF-8')
f.write(o[:-1])