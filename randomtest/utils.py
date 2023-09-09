from django.template.loader import get_template
from django.db.models import Q
from django.conf import settings

from subprocess import Popen,PIPE
import subprocess
import tempfile
import os,os.path
import re
from zipfile import ZipFile

#center,asy,enumerate,itemize, (tikzpicture), (includegraphics)
#class ItemizeEnv:
#    def __init__(self,itemize_code):

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
        return [(starts[i],ends[i]) for i in range(0,min(len(ends),len(starts)))]
    else:
        starts=indexesof('\\begin{'+latextag+'}['+optional+']',s)
        ends=[]
        for i in range(0,len(starts)):
            if '\\end{'+latextag+'}' in s[starts[i]:]:
                ends.append(s[starts[i]:].index('\\end{'+latextag+'}')+starts[i])
        return [(starts[i],ends[i]) for i in range(0,min(len(starts),len(ends)))]

def firstleveltagindexpairs(latextag,s,optional=''):
    if optional=='':
        starts = indexesof('\\begin{'+latextag+'}',s)
        ends = indexesof('\\end{'+latextag+'}',s)
    else:
        starts=indexesof('\\begin{'+latextag+'}['+optional+']',s)
        ends=[]
        for i in range(0,len(starts)):
            if '\\end{'+latextag+'}' in s[starts[i]:]:
                ends.append(s[starts[i]:].index('\\end{'+latextag+'}')+starts[i])
    if len(starts) == 0:
        return []
    firstlevelstarts = [starts[0]]
    firstlevelends = []
    level = 1
    startindex = 1
    endindex = 0
    while startindex < len(starts):
        if starts[startindex] < ends[endindex]:
            startindex += 1
            level += 1
        else:
            level -= 1
            if level == 0:
                firstlevelends.append(ends[endindex])
                firstlevelstarts.append(starts[startindex])
                startindex += 1
                level += 1
            endindex += 1
    while endindex < len(ends):
        level -=1
        if level == 0:
            firstlevelends.append(ends[endindex])
        endindex += 1
    return [(firstlevelstarts[i],firstlevelends[i]) for i in range(0,min(len(firstlevelends),len(firstlevelstarts)))]


def asyreplacementindexes(s):
    asys=tagindexpairs('asy',s)
    replacementpairs=[]
    for i in range(0,len(asys)):
        startindex=asys[i][0]
        endindex=asys[i][1]+9
        replacementpairs.append((startindex,endindex))
    return replacementpairs

def tikzreplacementindexes(s):
    tikzs=tagindexpairs('tikzpicture',s)
    replacementpairs=[]
    for i in range(0,len(tikzs)):
        startindex=tikzs[i][0]
        endindex=tikzs[i][1]+17
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


def itemenum_beginend_pop(s,start_index = 0):
    D = {}
    token = ""
    s_mod = s[start_index:]
    token_present = 0
    if '\\begin{enumerate}[' in s_mod:
        token_present = 1
        D['begin_enum_with_token'] = s_mod.index('\\begin{enumerate}[')+start_index
        start_here = s_mod[D['begin_enum_with_token']:]
        if ']' in start_here:
            token = start_here[start_here.index('[')+1:start_here.index(']')]
    if '\\begin{enumerate}' in s_mod:
        if token_present == 1:
            if s_mod.index('\\begin{enumerate}')+start_index < D['begin_enum_with_token']:
                D['begin_enum'] = s_mod.index('\\begin{enumerate}')+start_index
        else:
            D['begin_enum'] = s_mod.index('\\begin{enumerate}')+start_index
    if '\\begin{itemize}' in s_mod:
        D['begin_itemize'] = s_mod.index('\\begin{itemize}')+start_index
    if '\\end{enumerate}' in s_mod:
        D['end_enum'] = s_mod.index('\\end{enumerate}')+start_index
    if '\\end{itemize}' in s_mod:
        D['end_itemize'] = s_mod.index('\\end{itemize}')+start_index
    if '\\item ' in s_mod:
        D['item'] = s_mod.index('\\item ')+start_index
    min_index = -1
    name = ""
    for i in D:
        if min_index == -1 or D[i] < min_index:
            min_index = D[i]
            name = i
    return (name,min_index,token)

def replace_enumitem(s):
    t = itemenum_beginend_pop(s)
    r = ""
    level = 0
    enum_level = 0
    item_level = 0
    counter = 0
    current_pop_start = 0
    if t[0] != "" and t[0][0:4] == "begi":# only do stuff if the first delimiter is a begin.
        while t[0] != "":#pop til popping yields nothing
            t = itemenum_beginend_pop(s,current_pop_start)
            if level == 0 and t[0][0:4] == "begi":
                r += s[0:t[1]]#before the first environment opens, place in return string
                level +=1
                s = s[t[1]:]
                if t[0] == "begin_enum_with_token":
                    enum_level += 1
                    s = s[s.index(']')+1:]
                    current_pop_start = 0
                    if t[2] == '(i)':
                        r += "<ol class=\"par-list-lower-roman\">"
                    elif t[2] == '(a)':
                        r += "<ol class=\"par-list-lower-alpha\">"
                    elif t[2] == '(1)':
                        r += "<ol class=\"par-list-decimal\">"
                    elif t[2] == '(A)':
                        r += "<ol class=\"par-list-upper-alpha\">"
                    elif t[2] == '(I)':
                        r += "<ol class=\"par-list-upper-roman\">"
                    elif t[2] == 'i)':
                        r += "<ol class=\"right-par-list-lower-roman\">"
                    elif t[2] == 'a)':
                        r += "<ol class=\"right-par-list-lower-alpha\">"
                    elif t[2] == '1)':
                        r += "<ol class=\"right-par-list-decimal\">"
                    elif t[2] == 'A)':
                        r += "<ol class=\"right-par-list-upper-alpha\">"
                    elif t[2] == 'I)':
                        r += "<ol class=\"right-par-list-upper-roman\">"
                    elif t[2] == 'i.':
                        r += "<ol class=\"dot-list-lower-roman\">"
                    elif t[2] == 'a.':
                        r += "<ol class=\"dot-list-lower-alpha\">"
                    elif t[2] == '1.':
                        r += "<ol class=\"dot-list-decimal\">"
                    elif t[2] == 'A.':
                        r += "<ol class=\"dot-list-upper-alpha\">"
                    elif t[2] == 'I.':
                        r += "<ol class=\"dot-list-upper-roman\">"
                    else:
                        r += "<ol>"# work to be done...
                elif t[0] == "begin_enum":
                    enum_level += 1
                    s = s[s.index('}')+1:]
                    current_pop_start = 0
                    r += "<ol>"            
                elif t[0] == "begin_itemize":
                    item_level += 1
                    s = s[s.index('}')+1:]
                    current_pop_start = 0
                    r += "<ul>"
            t = itemenum_beginend_pop(s,current_pop_start)
            while level > 0 and t[0] != "":#does stuff until the enum/itemize gets closed/popping yields nothing
                t = itemenum_beginend_pop(s,current_pop_start)
                if t[0][0:4] == "item":#first, if items are in the current level, fix them up.
                    if level == 1:
                        if counter == 0:
                            r += s[0:t[1]] + '<li>'
                            s = s[t[1]+5:]# cut off \\item ; 
                            current_pop_start = 0
                            counter += 1
                        else:
                            r += s[0:t[1]] + '</li><li>'
                            s = s[t[1]+5:]
                            current_pop_start = 0
                            counter += 1
                    if level > 1:#if items are bad, move on to the next pop
                        current_pop_start = t[1] + 1
                if t[0][0:4] == "begi":
                    level += 1#always increase the level if popping is a new begin
                    if t[0] == "begin_enum_with_token":
                        enum_level += 1
                    elif t[0] == "begin_enum":
                        enum_level += 1
                    elif t[0] == "begin_itemize":
                        item_level += 1
                    if level == 2:#for the first nested situation.
                        level_two_start = t[1]
                    current_pop_start = t[1] + 1#move on to the next pop...
                if t[0][0:4] == "end_":
                    level -= 1# always decrease a level
                    if t[0] == "end_enum":
                        enum_level -= 1
                    elif t[0] == "end_itemize":
                        item_level -= 1
                    if level == 1:
                        if t[0] == 'end_enum':
                            level_two_end = t[1] + 15
                        else:
                            level_two_end = t[1] + 13
                        r += s[0:level_two_start]
                        r += replace_enumitem(s[level_two_start:level_two_end])
                        s = s[level_two_end:]
                        current_pop_start = 0
                    elif level == 0:
                        if t[0] == 'end_enum':
                            r += s[0:t[1]]+'</li></ol>'
                            s = s[t[1]+15:]
                            current_pop_start = 0
                            counter = 0
                        elif t[0] == 'end_itemize':
                            r += s[0:t[1]]+'</li></ul>'
                            s = s[t[1]+13:]
                            current_pop_start = 0
                            counter = 0
                    elif level > 1:
                        current_pop_start = t[1]+1
        return r+s[0:]
    else:
        return s
    return s
            
#perhaps include '\\item' in the above parser...


#def replacecenter(s):
#    if '\\begin{center}' not in s:
#        return s
#    r = s[0:s.index('\\begin{center}')]
#    while '\\begin{center}' in s and '\\end'
#    r = s[0:centers[0][0]]
#    for i in range(0,len(centers)-1):
#        middle = s[centers[i][0]+14:centers[i][1]]
#        
#<div id="mc_prob_text-{{prob.pk}}">
        

####Strategy: pop off the first begin (itemize/enumerate); keep on popping off the next begin/end.
def replaceitemize(s):
#    itemizes=tagindexpairs('itemize',s)
    itemizes = firstleveltagindexpairs('itemize',s)
    if len(itemizes)==0:
        return s
    r=s[0:itemizes[0][0]]
    for i in range(0,len(itemizes)-1):# this code has issues with nesting...partially an issue with tag index pairs
        middle=s[itemizes[i][0]+15:itemizes[i][1]]
        middle_itemizes = firstleveltagindexpairs('itemize',middle)
        if len(middle_itemizes) == 0:
            middle="<ul>"+middle.replace('\\item','<li>')+"</ul>"
            middlelist=middle.split("<li")
            mid=middlelist[0]
            for j in range(1,len(middlelist)-1):
                mid+="<li"+middlelist[j]+"</li>"
            mid+="<li"+middlelist[-1]
            mid=mid.replace('</ul>','</li></ul>')
            end=s[itemizes[i][1]+13:itemizes[i+1][0]]
            r+=mid+end
        else:
            mid_start = "<ul>" + middle[0:middle_itemizes[0][0]].replace("\\item","<li>")
            mid_start_list = mid_start.split("<li")
            beg = mid_start_list[0]
            for j in range(1,len(mid_start_list)-1):
                beg += "<li"+mid_start_list[j]+"</li>"
            beg + "<li"+mid_start_list[-1]
            r += beg
#            for k in range(0,len(middle_itemizes)):
                


    middle=s[itemizes[-1][0]:itemizes[-1][1]+13]
    middle=middle.replace('\\begin{itemize}','<ul>').replace('\\end{itemize}','</ul>').replace('\\item','<li>')
    middlelist=middle.split("<li")
    mid=middlelist[0]
    for j in range(1,len(middlelist)-1):
        mid+="<li"+middlelist[j]+"</li>"
    mid+="<li"+middlelist[-1]
    mid=mid.replace('</ul>','</li></ul>')
    end=s[itemizes[-1][1]+13:]
    r+=mid+'\n'+end
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
            middlelist=middle.split("<li")
            mid=middlelist[0]
            for j in range(1,len(middlelist)-1):
                mid+="<li"+middlelist[j]+"</li>"
            mid+="<li"+middlelist[-1]
            mid=mid.replace('</ol>','</li></ol>')
            end=s[enums[i][1]+15:enums[i+1][0]]
            r+=mid+end
        middle=s[enums[-1][0]:enums[-1][1]+15]
        middle=middle.replace('\\begin{enumerate}','<ol>').replace('\\end{enumerate}','</ol>').replace('\\item ','<li>').replace('\\item[(a)]','<li type=\"a\">').replace('\\item[(b)]','<li type=\"a\">').replace('\\item[(c)]','<li type=\"a\">').replace('\\item[(d)]','<li type=\"a\">').replace('\\item[(e)]','<li type=\"a\">').replace('\\item[(i)]','<li type=\"i\">').replace('\\item[(ii)]','<li type=\"i\">').replace('\\item[(iii)]','<li type=\"i\">').replace('\\item[(iv)]','<li type=\"i\">').replace('\\item[(v)]','<li type=\"i\">')
        middlelist=middle.split("<li")
        mid=middlelist[0]
        for j in range(1,len(middlelist)-1):
            mid+="<li"+middlelist[j]+"</li>"
        mid+="<li"+middlelist[-1]
        mid=mid.replace('</ol>','</li></ol>')
        end=s[enums[-1][1]+15:]
        r+=mid+'\n'+end
        return r
    else:
        if '(' in optional:
            parentheses = True
        token = optional.replace(')','').replace('(','').replace('.','')
        token = ""
        r=s[0:enums[0][0]]
        for i in range(0,len(enums)-1):
            middle=s[enums[i][0]:enums[i][1]+15]
            if parentheses == False:
                middle=middle.replace('\\begin{enumerate}['+optional+']','<ol>')
#                middle=middle.replace('\\begin{enumerate}['+optional+']','<ol type=\"'+optional.replace(')','').replace('(','').replace('.','')+'\">')
            else:
                middle=middle.replace('\\begin{enumerate}['+optional+']','<ol class=\"parentheses-list\"'+'>')
 #               middle=middle.replace('\\begin{enumerate}['+optional+']','<ol class=\"parentheses-list\" type=\"'+optional.replace(')','').replace('(','').replace('.','')+'\">')
            middle = middle.replace('\\end{enumerate}','</ol>').replace('\\item ','<li type=\"'+token+'\">').replace('\\item[(1)]','<li type=\"'+token+'\">').replace('\\item[(2)]','<li type=\"'+token+'\">').replace('\\item[(3)]','<li type=\"'+token+'\">').replace('\\item[(4)]','<li type=\"'+token+'\">').replace('\\item[(5)]','<li type=\"'+token+'\">').replace('\\item[(a)]','<li type=\"'+token+'\">').replace('\\item[(b)]','<li type=\"'+token+'\">').replace('\\item[(c)]','<li type=\"'+token+'\">').replace('\\item[(d)]','<li type=\"'+token+'\">').replace('\\item[(e)]','<li type=\"'+token+'\">').replace('\\item[(i)]','<li type=\"'+token+'\">').replace('\\item[(ii)]','<li type=\"'+token+'\">').replace('\\item[(iii)]','<li type=\"'+token+'\">').replace('\\item[(iv)]','<li type=\"'+token+'\">').replace('\\item[(v)]','<li type=\"'+token+'\">')
            middlelist=middle.split("<li")
            mid=middlelist[0]
            for j in range(1,len(middlelist)-1):
                mid+="<li"+middlelist[j]+"</li>"
            mid+="<li"+middlelist[-1]
            mid=mid.replace('</ol>','</li></ol>')
            end=s[enums[i][1]+15:enums[i+1][0]]
            r+=mid+end
        middle=s[enums[-1][0]:enums[-1][1]+15]
        if parentheses == False:
            middle=middle.replace('\\begin{enumerate}['+optional+']','<ol>')
#            middle=middle.replace('\\begin{enumerate}['+optional+']','<ol type=\"'+optional.replace(')','').replace('(','').replace('.','')+'\">')
        else:
            middle=middle.replace('\\begin{enumerate}['+optional+']','<ol class=\"parentheses-list\" >')
#            middle=middle.replace('\\begin{enumerate}['+optional+']','<ol class=\"parentheses-list\" type=\"'+optional.replace(')','').replace('(','').replace('.','')+'\">')

        middle=middle.replace('\\end{enumerate}','</ol>').replace('\\item ','<li type=\"'+token+'\">').replace('\\item[(1)]','<li type=\"'+token+'\">').replace('\\item[(2)]','<li type=\"'+token+'\">').replace('\\item[(3)]','<li type=\"'+token+'\">').replace('\\item[(4)]','<li type=\"'+token+'\">').replace('\\item[(5)]','<li type=\"'+token+'\">').replace('\\item[(a)]','<li type=\"'+token+'\">').replace('\\item[(b)]','<li type=\"'+token+'\">').replace('\\item[(c)]','<li type=\"'+token+'\">').replace('\\item[(d)]','<li type=\"'+token+'\">').replace('\\item[(e)]','<li type=\"'+token+'\">').replace('\\item[(i)]','<li type=\"'+token+'\">').replace('\\item[(ii)]','<li type=\"'+token+'\">').replace('\\item[(iii)]','<li type=\"'+token+'\">').replace('\\item[(iv)]','<li type=\"'+token+'\">').replace('\\item[(v)]','<li type=\"'+token+'\">')
        middlelist=middle.split("<li")
        mid=middlelist[0]
        for j in range(1,len(middlelist)-1):
            mid+="<li"+middlelist[j]+"</li>"
        mid+="<li"+middlelist[-1]
        mid=mid.replace('</ol>','</li></ol>')
        end=s[enums[-1][1]+15:]
        r+=mid+'\n'+end
        return r

def newtexcode(texcode,label,answer_choices,temp = False):
    texcode = texcode.replace('<',' < ')
    repl = asyreplacementindexes(texcode)
    newtexcode=''
    tempdir = ''
    if temp == True:
        tempdir = 'temp/'
    if len(repl)==0:
        newtexcode+=texcode
    else:
        newtexcode+=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            three=''
            if 'import three' in texcode[repl[i][0]:repl[i][1]] or 'import graph3' in texcode[repl[i][0]:repl[i][1]]:
                three='+0_0'
            newtexcode+='<img class=\"displayed\" src=\"/media/'+tempdir+label+'-'+str(i+1)+three+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        three=''
        if 'import three' in texcode[repl[-1][0]:repl[-1][1]] or 'import graph3' in texcode[repl[-1][0]:repl[-1][1]]:
            three='+0_0'
        newtexcode+='<img class=\"displayed\" src=\"/media/'+tempdir+label+'-'+str(len(repl))+three+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]

    repl2 = tikzreplacementindexes(newtexcode)
    new2texcode = ''

    if len(repl2) == 0:
        new2texcode += newtexcode
    else:
        new2texcode += newtexcode[0:repl2[0][0]]
        for i in range(0,len(repl2)-1):
            new2texcode += '<img class=\"inline-displayed\" src=\"/media/'+tempdir+'tikz'+label+'-'+str(i+1)+'.png\"/>'
            new2texcode += newtexcode[repl2[i][1]:repl2[i+1][0]]
        new2texcode+='<img class=\"inline-displayed\" src=\"/media/'+tempdir+'tikz'+label+'-'+str(len(repl2))+'.png\"/>'
        new2texcode+=texcode[repl2[-1][1]:]
    newtexcode = new2texcode
    newtexcode += '<br><br>'+ansscrape(answer_choices)
    newtexcode = newtexcode.replace('\\ ',' ')
#    newtexcode=replaceitemize(newtexcode)
#    newtexcode=replaceenumerate(newtexcode,'(a)')
#    newtexcode=replaceenumerate(newtexcode,'(i)')
#    newtexcode=replaceenumerate(newtexcode)
    newtexcode = replace_enumitem(newtexcode)

    newtexcode = newtexcode.replace('\\begin{center}','<p style="text-align:center;\">')####dangerous....
    newtexcode = newtexcode.replace('\\end{center}','</p>\n')

    return newtexcode

def newsoltexcode(texcode,label):
    texcode = texcode.replace('<',' < ')
    repl = asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode+=texcode
    else:
        newtexcode+=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            three=''
            if 'import three' in texcode[repl[i][0]:repl[i][1]] or 'import graph3' in texcode[repl[i][0]:repl[i][1]]:
                three='+0_0'
            newtexcode+='<img class=\"displayed\" src=\"/media/'+label+'-'+str(i+1)+three+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        three=''
        if 'import three' in texcode[repl[-1][0]:repl[-1][1]] or 'import graph3' in texcode[repl[-1][0]:repl[-1][1]]:
            three='+0_0'
        newtexcode+='<img class=\"displayed\" src=\"/media/'+label+'-'+str(len(repl))+three+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]

#    newtexcode=replaceitemize(newtexcode)
#    newtexcode=replaceenumerate(newtexcode,'(a)')
#    newtexcode=replaceenumerate(newtexcode,'(i)')
#    newtexcode=replaceenumerate(newtexcode)

    repl2 = tikzreplacementindexes(newtexcode)
    new2texcode = ''
    if len(repl2) == 0:
        new2texcode += newtexcode
    else:
        new2texcode += newtexcode[0:repl2[0][0]]
        for i in range(0,len(repl2)-1):
            new2texcode += '<img class=\"inline-displayed\" src=\"/media/tikz'+label+'-'+str(i+1)+'.png\"/>'
            new2texcode += newtexcode[repl2[i][1]:repl2[i+1][0]]
        new2texcode+='<img class=\"inline-displayed\" src=\"/media/tikz'+label+'-'+str(len(repl2))+'.png\"/>'
        new2texcode+=texcode[repl2[-1][1]:]
    newtexcode = new2texcode

    newtexcode = replace_enumitem(newtexcode)

    newtexcode = newtexcode.replace('\\begin{center}','<p style="text-align:center;\">')
    newtexcode = newtexcode.replace('\\end{center}','</p>\n')
    return newtexcode

def newcomtexcode(texcode):
    texcode = texcode.replace('<',' < ')
    newtexcode = texcode.replace('\\ ',' ')
    newtexcode = replace_enumitem(newtexcode)
    newtexcode = newtexcode.replace('\\begin{center}','<p style="text-align:center;\">')####dangerous....
    newtexcode = newtexcode.replace('\\end{center}','</p>\n')
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


def compileasy(texcode, label, sol = '', temp = False):
    tempfolder = ''
    if temp == True:
        tempfolder = 'temp/'
    repl = asyreplacementindexes(texcode)
    error = ''
    for i in range(0,len(repl)):
        asy_code = texcode[repl[i][0]:repl[i][1]]
        asy_code = asy_code.replace('\\begin{asy}','')
        asy_code = asy_code.replace('\\begin{center}','<center>')
        asy_code = asy_code.replace('\\end{asy}','')
        asy_code = asy_code.replace('\\end{center}','</center>')
        asy_code = asy_code.rstrip().lstrip()
        filename = label+sol+'-'+str(i+1)
        context = {
            'asy_code':asy_code,
            'filename':filename,
            }
        template = get_template('asycompile/my_asy_template.asy')
        rendered_tpl = template.render(context).encode('utf-8')
        with tempfile.TemporaryDirectory() as tempdir:
            asy_file = open(os.path.join(tempdir,'asyput.asy'),'wb')
            asy_file.write(rendered_tpl)
            asy_file.close()
            process = Popen(
                ['asy', '-o', os.path.join(tempdir,filename+'.pdf'), tempdir+'/asyput.asy'],
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                )
            check_error = process.communicate(rendered_tpl)[1].decode("utf-8").replace("GC Warning: pthread_getattr_np or pthread_attr_getstack failed for main thread","").rstrip().lstrip()
            if check_error != "":
                error = check_error
            L = os.listdir(tempdir)
            for j in L:
                if 'pdf' in j:
                    command = "pdftoppm -png %s/%s > %s%s" % (tempdir, j, settings.MEDIA_ROOT+tempfolder, j.replace('.pdf','.png'))
                    proc = subprocess.Popen(command,
                                            shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            )
                    stdout_value = proc.communicate()[0]
    return error

def compiletikz(texcode,label,sol='',temp = False):
    tempfolder = ''
    if temp == True:
        tempfolder = 'temp/'
    repl = tikzreplacementindexes(texcode)
    for i in range(0,len(repl)):
        tikz_code = texcode[repl[i][0]:repl[i][1]]
        tikz_code = tikz_code.rstrip().lstrip()
        filename = 'tikz'+label+sol+'-'+str(i+1)
        filename = filename.replace(' ','')
        context = {
            'tikz_code':tikz_code,
            'filename':filename,
            }
        template = get_template('randomtest/my_tikz_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')


        with tempfile.TemporaryDirectory() as tempdir:
            ftex=open(os.path.join(tempdir,'texput.tex'),'wb')
            ftex.write(rendered_tpl)
            ftex.close()
            for j in range(0,2):
                process = Popen(
                    ['pdflatex', 'texput.tex'],
                    stdin=PIPE,
                    stdout=PIPE,
                    cwd = tempdir,
                    )
                process.communicate(rendered_tpl)
            t=os.getcwd()
            os.chdir(tempdir)
            command = "mtxrun --script pdftrimwhite --offset=10 texput.pdf texput-2.pdf"
            proc1 = subprocess.Popen(command,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    )
            stdout_value = proc1.communicate()[0]
            os.chdir(t)
            command = "pdftoppm -png %s/%s > %s%s" % (tempdir, 'texput-2.pdf', settings.MEDIA_ROOT+tempfolder, filename + '.png')
            proc = subprocess.Popen(command,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    )
            stdout_value = proc.communicate()[0]


def pointsum(user_responses):
    tot=0
    for i in user_responses:
        tot+=i.point_value
    return tot

def sorted_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)







def make_all_pngs(L,include_problem_labels = False,include_answer_choices = True):
    temps = []
    for prob in L:
        ptext = ''
        if prob.question_type_new.question_type == 'multiple choice' or prob.question_type_new.question_type == 'multiple choice short answer':
            ptext = prob.mc_problem_text
            answers = prob.answers()
        else:
            ptext = prob.problem_text
            answers = ''
        context = {
            'prob':prob,
            'problemcode':ptext,
            'problemlabel':prob.readable_label,
            'answerchoices': answers,
            'pk':prob.pk,
            'include_problem_labels':include_problem_labels,
        }
        asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
        asyr = asyf.read()
        asyf.close()
        template = get_template('problemeditor/my_singleproblem_latex_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        temps.append(rendered_tpl)

    with tempfile.TemporaryDirectory() as tempdir:
        fa=open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        for prob in L:
            ptext = ''
            if prob.question_type_new.question_type == 'multiple choice' or prob.question_type_new.question_type == 'multiple choice short answer':
                ptext = prob.mc_problem_text
                answers = prob.answers()
            else:
                ptext = prob.problem_text
                answers = ''
            context = {
                'prob' : prob,
                'problemcode' : ptext,
                'problemlabel' : prob.readable_label,
                'pk':prob.pk,
                'include_problem_labels':include_problem_labels,
                'include_answer_choices':include_answer_choices,
                'answerchoices':answers,
                'tempdirect':tempdir,
            }
            template = get_template('problemeditor/my_singleproblem_latex_template.tex')
            rendered_tpl = template.render(context).encode('utf-8')
            ftex=open(os.path.join(tempdir,'texput.tex'),'wb')
            ftex.write(rendered_tpl)
            ftex.close()
            for i in range(1):
                process = Popen(
                    ['pdflatex', 'texput.tex'],
                    stdin=PIPE,
                    stdout=PIPE,
                    cwd = tempdir,
                )
                stdout_value = process.communicate()[0]
            LL=os.listdir(tempdir)

            for i in range(0,len(LL)):
                if LL[i][-4:]=='.asy':
                    process1 = Popen(
                        ['asy', LL[i]],
                        stdin = PIPE,
                        stdout = PIPE,
                        cwd = tempdir,
                    )
                    stdout_value = process1.communicate()[0]
            for i in range(2):
                process2 = Popen(
                    ['pdflatex', 'texput.tex'],
                    stdin=PIPE,
                    stdout=PIPE,
                    cwd = tempdir,
                )
                stdout_value = process2.communicate()[0]
            command = "pdfcrop --margin 5 %s/%s  %s/%s" % (tempdir, 'texput.pdf', tempdir,'newtexput.pdf')
            proc = subprocess.Popen(command,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
            )
            stdout_value = proc.communicate()[0]

            command = "pdftoppm -png %s/%s > %s/%s" % (tempdir, 'newtexput.pdf', tempdir, prob.label+'.png')
            proc = subprocess.Popen(command,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
            )
            stdout_value = proc.communicate()[0]
        with ZipFile("output.zip",'w') as myzip:
            for prob in L:
                myzip.write(tempdir+'/'+prob.label+'.png')
#    for p in L:
#        os.system("convert -density 150 "+p.label+'.pdf -quality 100 -trim -bordercolor White -border 10x10 +repage '+p.label+'.jpg')
