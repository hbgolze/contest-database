
def parsebool(tags):
    if '|' in tags and '&' not in tags:
        l=tags.split('|')
        return ('or',l)
    elif '&' in tags and '|' not in tags:
        l=tags.split('&')
        return ('and',l)
    else:
        return ('or',[tags])

def indexesof(k,target):
    if target.count(k)==0:
        return []
    if target.count(k)==1:
        return [target.index(k)]
    x=indexesof(k,target[target.index(k)+1:])
    x=[x[i]+target.index(k)+1 for i in range(0,len(x))]
    x.append(target.index(k))
    x.sort()
    return x

def tagindexpairs(latextag,s):
    starts=indexesof('\\begin{'+latextag+'}',s)
    ends=indexesof('\\end{'+latextag+'}',s)
    return [(starts[i],ends[i]) for i in range(0,len(starts))]

def asyreplacementindexes(s):
    centers=tagindexpairs('center',s)
    asys=tagindexpairs('asy',s)
    replacementpairs=[]
    for i in range(0,len(asys)):
        startindex=asys[i][0]
        endindex=asys[i][1]+9
        for j in range(0,len(centers)):
            if asys[i][0]>centers[j][0] and asys[i][1]<centers[j][1]:
                startindex=centers[j][0]
                endindex=centers[j][1]+12
        replacementpairs.append((startindex,endindex))
    return replacementpairs
                
def ansscrape(s):
    if 'begin{ans}' not in s:
        return s
    opens=indexesof('{',s)
    closes=indexesof('}',s)
    openup=opens[1]
    all=opens+closes
    all.sort()
    closer=-1
    for j in range(1,len(closes)-1):
        if opens[j+1]>closes[j]:
            closer=closes[j]
            break
    return s[closer+1:s.index('\\end{ans}')]

def goodurl(t):
    return t.replace('>','_').replace(' ','~')
def goodtag(t):
    return t.replace('_','>').replace('~',' ')
