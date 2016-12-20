
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

#this may need to be modified due to potential user coding errors (in LaTeX)
def tagindexpairs(latextag,s,optional=''):
    if optional=='':
        starts=indexesof('\\begin{'+latextag+'}',s)
        ends=indexesof('\\end{'+latextag+'}',s)
        return [(starts[i],ends[i]) for i in range(0,len(starts))]
    else:
        starts=indexesof('\\begin{'+latextag+'}['+optional+']',s)
        ends=[]
        for i in range(0,len(starts)):
            if '\\end{'+latextag+'}' in s[starts[i]:]:
                ends.append(s[starts[i]:].index('\\end{'+latextag+'}')+starts[i])
        return [(starts[i],ends[i]) for i in range(0,len(ends))]


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

def replaceitemize(s):
    itemizes=tagindexpairs('itemize',s)
    if len(itemizes)==0:
        return s
    r=s[0:itemizes[0][0]]
    for i in range(0,len(itemizes)-1):
        middle=s[itemizes[i][0]:itemizes[i][1]+13]
        middle=middle.replace('\\begin{itemize}','<ul>').replace('\\end{itemize}','</ul>').replace('\\item','<li>')
        end=s[itemizes[i][1]+13:itemizes[i+1][0]]
        r+=middle+end
    middle=s[itemizes[-1][0]:itemizes[-1][1]+13]
    middle=middle.replace('\\begin{itemize}','<ul>').replace('\\end{itemize}','</ul>').replace('\\item','<li>')
    end=s[itemizes[-1][1]+13:]
    r+=middle+end
    return r

def replaceenumerate(s,optional=''):
    enums=tagindexpairs('enumerate',s,optional)
    if len(enums)==0:
        return s
    if optional=='':
        r=s[0:enums[0][0]]
        for i in range(0,len(enums)-1):
            middle=s[enums[i][0]:enums[i][1]+15]
            middle=middle.replace('\\begin{enumerate}','<ol>').replace('\\end{enumerate}','</ol>').replace('\\item ','<li>').replace('\\item[(a)]','<li type=\"a\">').replace('\\item[(b)]','<li type=\"a\">').replace('\\item[(c)]','<li type=\"a\">').replace('\\item[(d)]','<li type=\"a\">').replace('\\item[(e)]','<li type=\"a\">').replace('\\item[(i)]','<li type=\"i\">').replace('\\item[(ii)]','<li type=\"i\">').replace('\\item[(iii)]','<li type=\"i\">').replace('\\item[(iv)]','<li type=\"i\">').replace('\\item[(v)]','<li type=\"i\">')
            end=s[enums[i][1]+15:enums[i+1][0]]
            r+=middle+end
        middle=s[enums[-1][0]:enums[-1][1]+15]
        middle=middle.replace('\\begin{enumerate}','<ol>').replace('\\end{enumerate}','</ol>').replace('\\item ','<li>').replace('\\item[(a)]','<li type=\"a\">').replace('\\item[(b)]','<li type=\"a\">').replace('\\item[(c)]','<li type=\"a\">').replace('\\item[(d)]','<li type=\"a\">').replace('\\item[(e)]','<li type=\"a\">').replace('\\item[(i)]','<li type=\"i\">').replace('\\item[(ii)]','<li type=\"i\">').replace('\\item[(iii)]','<li type=\"i\">').replace('\\item[(iv)]','<li type=\"i\">').replace('\\item[(v)]','<li type=\"i\">')
        end=s[enums[-1][1]+15:]
        r+=middle+end
        return r
    else:
        token = optional.replace(')','').replace('(','').replace('.','')
        r=s[0:enums[0][0]]
        for i in range(0,len(enums)-1):
            middle=s[enums[i][0]:enums[i][1]+15]
            middle=middle.replace('\\begin{enumerate}['+optional+']','<ol type=\"'+optional.replace(')','').replace('(','').replace('.','')+'\">').replace('\\end{enumerate}','</ol>').replace('\\item ','<li type=\"'+token+'\">').replace('\\item[(1)]','<li type=\"'+token+'\">').replace('\\item[(2)]','<li type=\"'+token+'\">').replace('\\item[(3)]','<li type=\"'+token+'\">').replace('\\item[(4)]','<li type=\"'+token+'\">').replace('\\item[(5)]','<li type=\"'+token+'\">').replace('\\item[(a)]','<li type=\"'+token+'\">').replace('\\item[(b)]','<li type=\"'+token+'\">').replace('\\item[(c)]','<li type=\"'+token+'\">').replace('\\item[(d)]','<li type=\"'+token+'\">').replace('\\item[(e)]','<li type=\"'+token+'\">').replace('\\item[(i)]','<li type=\"'+token+'\">').replace('\\item[(ii)]','<li type=\"'+token+'\">').replace('\\item[(iii)]','<li type=\"'+token+'\">').replace('\\item[(iv)]','<li type=\"'+token+'\">').replace('\\item[(v)]','<li type=\"'+token+'\">')
            end=s[enums[i][1]+15:enums[i+1][0]]
            r+=middle+end
        middle=s[enums[-1][0]:enums[-1][1]+15]
        middle=middle.replace('\\begin{enumerate}['+optional+']','<ol type=\"'+optional.replace(')','').replace('(','').replace('.','')+'\">').replace('\\end{enumerate}','</ol>').replace('\\item ','<li type=\"'+token+'\">').replace('\\item[(1)]','<li type=\"'+token+'\">').replace('\\item[(2)]','<li type=\"'+token+'\">').replace('\\item[(3)]','<li type=\"'+token+'\">').replace('\\item[(4)]','<li type=\"'+token+'\">').replace('\\item[(5)]','<li type=\"'+token+'\">').replace('\\item[(a)]','<li type=\"'+token+'\">').replace('\\item[(b)]','<li type=\"'+token+'\">').replace('\\item[(c)]','<li type=\"'+token+'\">').replace('\\item[(d)]','<li type=\"'+token+'\">').replace('\\item[(e)]','<li type=\"'+token+'\">').replace('\\item[(i)]','<li type=\"'+token+'\">').replace('\\item[(ii)]','<li type=\"'+token+'\">').replace('\\item[(iii)]','<li type=\"'+token+'\">').replace('\\item[(iv)]','<li type=\"'+token+'\">').replace('\\item[(v)]','<li type=\"'+token+'\">')
        end=s[enums[-1][1]+15:]
        r+=middle+end
        return r

def newtexcode(texcode,dropboxpath,label,answer_choices):
    repl=asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode+=texcode
    else:
        newtexcode+=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(i+1)+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(len(repl))+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]
    newtexcode+='<br><br>'+ansscrape(answer_choices)
    newtexcode=newtexcode.replace('\\ ',' ')
    newtexcode=replaceitemize(newtexcode)
    newtexcode=replaceenumerate(newtexcode,'(a)')
    newtexcode=replaceenumerate(newtexcode,'(i)')
    newtexcode=replaceenumerate(newtexcode)
    return newtexcode

def compileasy(s,label):
    repl = asyreplacementindices(texcode)
    #create a template for asy code; then compile it in  folder. But it must be able to be cleaned up.
                
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
    return t.replace('>','_').replace(' ','__')
def goodtag(t):
    return t.replace('__',' ').replace('_','>')
