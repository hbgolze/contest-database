from django.template import Context

from django.template.loader import get_template

from django.db.models import Q
#from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Dropboxurl,Comment,QuestionType,ProblemApproval
from django.conf import settings

from subprocess import Popen,PIPE
import subprocess
import tempfile
import os,os.path

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
    asys=tagindexpairs('asy',s)
    replacementpairs=[]
    for i in range(0,len(asys)):
        startindex=asys[i][0]
        endindex=asys[i][1]+9
        replacementpairs.append((startindex,endindex))
    return replacementpairs

def centerasyreplacementindexes(s):
    centers=tagindexpairs('center',s)
    asys=tagindexpairs('asy',s)
    replacementpairs=[]
    for i in range(0,len(centers)):
        startindex=centers[i][0]
        endindex=centers[i][1]+12
        if '\\begin{asy}' in s[startindex:endindex]:
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
    r+=middle+'\n'+end
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
        r+=middle+'\n'+end
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
        r+=middle+'\n'+end
        return r

def newtexcode(texcode,dropboxpath,label,answer_choices):
    texcode=texcode.replace('<',' < ')
    repl=asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode+=texcode
    else:
        newtexcode+=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            three=''
            if 'import three' in texcode[repl[i][0]:repl[i][1]]:
                three='+0_0'
            newtexcode+='<img class=\"displayed\" src=\"/media/'+label+'-'+str(i+1)+three+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        three=''
        if 'import three' in texcode[repl[-1][0]:repl[-1][1]]:
            three='+0_0'
        newtexcode+='<img class=\"displayed\" src=\"/media/'+label+'-'+str(len(repl))+three+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]
    newtexcode+='<br><br>'+ansscrape(answer_choices)
    newtexcode=newtexcode.replace('\\ ',' ')
    newtexcode=replaceitemize(newtexcode)
    newtexcode=replaceenumerate(newtexcode,'(a)')
    newtexcode=replaceenumerate(newtexcode,'(i)')
    newtexcode=replaceenumerate(newtexcode)
    newtexcode=newtexcode.replace('\\begin{center}','')
    newtexcode=newtexcode.replace('\\end{center}','\n')
    return newtexcode

def newsoltexcode(texcode,dropboxpath,label):
    texcode=texcode.replace('<',' < ')
    repl=asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode+=texcode
    else:
        newtexcode+=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            newtexcode+='<img class=\"displayed\" src=\"/media/'+label+'-'+str(i+1)+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        newtexcode+='<img class=\"displayed\" src=\"/media/'+label+'-'+str(len(repl))+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]
    newtexcode=replaceitemize(newtexcode)
    newtexcode=replaceenumerate(newtexcode,'(a)')
    newtexcode=replaceenumerate(newtexcode,'(i)')
    newtexcode=replaceenumerate(newtexcode)
    newtexcode=newtexcode.replace('\\begin{center}','')
    newtexcode=newtexcode.replace('\\end{center}','\n')
    return newtexcode

                
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


def compileasy(texcode,label,sol=''):
    repl = asyreplacementindexes(texcode)
    for i in range(0,len(repl)):
        asy_code = texcode[repl[i][0]:repl[i][1]]
        asy_code = asy_code.replace('\\begin{asy}','')
        asy_code = asy_code.replace('\\begin{center}','<center>')
        asy_code = asy_code.replace('\\end{asy}','')
        asy_code = asy_code.replace('\\end{center}','</center>')
        asy_code = asy_code.rstrip().lstrip()
        filename = label+sol+'-'+str(i+1)
        context = Context({
                'asy_code':asy_code,
                'filename':filename,
                })
        template = get_template('asycompile/my_asy_template.asy')
        rendered_tpl = template.render(context).encode('utf-8')
        with tempfile.TemporaryDirectory() as tempdir:
            process = Popen(
                ['asy', '-o', os.path.join(tempdir,filename+'.pdf')],
                stdin=PIPE,
                stdout=PIPE,
                )
            process.communicate(rendered_tpl)
            L=os.listdir(tempdir)
            for j in L:
                if 'pdf' in j:
                    command = "convert -density 150 -quality 95 %s/%s %s%s" % (tempdir, j, settings.MEDIA_ROOT, j.replace('.pdf','.png'))
                    proc = subprocess.Popen(command,
                                            shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            )
                    stdout_value = proc.communicate()[0]
