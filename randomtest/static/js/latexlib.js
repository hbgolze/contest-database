function indexesof(k,target) {
    if (target.indexOf(k)==-1) {
        return [];
    }
    if (target.substring(target.indexOf(k)+1).indexOf(k) == -1) {
	return [target.indexOf(k)];
    }
    var x = indexesof(k,target.substring(target.indexOf(k)+1));
    var y = [];
    var i;
    for (i=0; i < x.length; i++) {
        y.push(x[i]+target.indexOf(k)+1);
    }
    y.push(target.indexOf(k));
    y.sort((a, b) => a - b);
    return y;
}

function tagindexpairs(latextag,s,optional='') {
    if (optional == '') {
	var starts = indexesof('\\begin{'+latextag+'}',s);
	var ends = indexesof('\\end{'+latextag+'}',s);
	var ret =[];
	var i;
	for (i =0; i < Math.min(ends.length,starts.length);i++) {
	    ret.push([starts[i],ends[i]]);
	}
	return ret;
    }
    else {
        var starts = indexesof('\\begin{'+latextag+'}['+optional+']',s);
        var ends = [];
	var ret = [];
	var i;
	for (i=0; i < starts.length; i++) {
            if (s.slice(starts[i]).indexOf('\\end{'+latextag+'}')!== -1) {
                ends.push(s.slice(starts[i]).indexOf('\\end{'+latextag+'}')+starts[i]);
	    }
	}
	for (i =0; i < Math.min(ends.length,starts.length);i++) {
	    ret.push([starts[i],ends[i]]);
	}
	return ret;
    }
}

function asyreplacementindexes(s) {
    var asys = tagindexpairs('asy',s);
    var replacementpairs = [];
    var i;
    for (i=0; i < asys.length; i++) {
        startindex = asys[i][0];
        endindex = asys[i][1]+9;
	replacementpairs.push([startindex,endindex]);
    }
    return replacementpairs;
}

function tikzreplacementindexes(s) {
    var tikzs = tagindexpairs('tikzpicture',s);
    var replacementpairs = [];
    for (i=0; i < tikzs.length; i++) {
        startindex = tikzs[i][0];
        endindex = tikzs[i][1]+17;
	replacementpairs.push([startindex,endindex]);
    }
    return replacementpairs;
}


function itemenum_beginend_pop(s,start_index = 0) {
    var D = {};
    var token = "";
    var s_mod = s.slice(start_index);//to end of string
    var token_present = 0;
    if (s_mod.indexOf('\\begin{enumerate}[') !==-1) {
	token_present = 1;
	D['begin_enum_with_token'] = s_mod.indexOf('\\begin{enumerate}[')+start_index;
	var start_here = s_mod.slice(D['begin_enum_with_token']);//to end of string
	if (start_here.indexOf(']') !==-1) {
            token = start_here.slice(start_here.indexOf('[')+1,start_here.indexOf(']'));
	}
    }
    if (s_mod.indexOf('\\begin{enumerate}') !==-1) {
	if (token_present == 1) {
	    if (s_mod.indexOf('\\begin{enumerate}')+start_index < D['begin_enum_with_token']) {
		D['begin_enum'] = s_mod.indexOf('\\begin{enumerate}')+start_index;
	    }
	} else {
	    D['begin_enum'] = s_mod.indexOf('\\begin{enumerate}')+start_index;
	}
    }

    if (s_mod.indexOf('\\begin{itemize}') !==-1) {
	D['begin_itemize'] = s_mod.indexOf('\\begin{itemize}')+start_index;
    }

    if (s_mod.indexOf('\\end{enumerate}') !==-1) {
	D['end_enum'] = s_mod.indexOf('\\end{enumerate}')+start_index;
    }    

    if (s_mod.indexOf('\\end{itemize}') !==-1) {
	D['end_itemize'] = s_mod.indexOf('\\end{itemize}')+start_index;
    }

    if (s_mod.indexOf('\\item ') !==-1) {
	D['item'] = s_mod.indexOf('\\item ')+start_index;
    }

    var min_index = -1;
    var name = "";
    for (var i in D) {
	if (min_index == -1 || D[i] < min_index) {
            min_index = D[i];
            name = i;
	}
    }

    return [name,min_index,token];
}

function replace_enumitem(s) {
    var t = itemenum_beginend_pop(s);
    var r = "";
    var level = 0;
    var enum_level = 0;
    var item_level = 0;
    var counter = 0;
    var current_pop_start = 0;
    if (t[0] != "" && t[0].slice(0,4) == "begi") {
	while (t[0] != "") {
	    t = itemenum_beginend_pop(s,current_pop_start);
	    if (level == 0 && t[0].slice(0,4) == "begi") {
		r += s.slice(0,t[1]);
		level +=1;
		s = s.slice(t[1]);
		if (t[0] == "begin_enum_with_token") {
                    enum_level += 1;
                    s = s.slice(s.indexOf(']')+1);
                    current_pop_start = 0;
                    if (t[2] == '(i)') {
                        r += "<ol class=\"par-list-lower-roman\">";
		    } else if (t[2] == '(a)') {
			r += "<ol class=\"par-list-lower-alpha\">";
		    } else if (t[2] == '(1)') {
			r += "<ol class=\"par-list-decimal\">";
		    } else if (t[2] == '(A)') {
                        r += "<ol class=\"par-list-upper-alpha\">";
		    } else if (t[2] == '(I)') {
                        r += "<ol class=\"par-list-upper-roman\">";
		    } else if (t[2] == 'i)') {
                        r += "<ol class=\"right-par-list-lower-roman\">";
		    } else if (t[2] == 'a)') {
			r += "<ol class=\"right-par-list-lower-alpha\">";
		    } else if (t[2] == '1)') {
                        r += "<ol class=\"right-par-list-decimal\">";
                    } else if (t[2] == 'A)') {
                        r += "<ol class=\"right-par-list-upper-alpha\">";
                    } else if (t[2] == 'I)') {
                        r += "<ol class=\"right-par-list-upper-roman\">";
                    } else if (t[2] == 'i.') {
                        r += "<ol class=\"dot-list-lower-roman\">";
                    } else if (t[2] == 'a.') {
                        r += "<ol class=\"dot-list-lower-alpha\">";
                    } else if (t[2] == '1.') {
                        r += "<ol class=\"dot-list-decimal\">";
                    } else if (t[2] == 'A.') {
                        r += "<ol class=\"dot-list-upper-alpha\">";
                    } else if (t[2] == 'I.') {
                        r += "<ol class=\"dot-list-upper-roman\">";
		    } else {
			r += "<ol>";
		    }
		} else if (t[0] == "begin_enum") {
		    enum_level += 1;
		    s = s.slice(s.indexOf('}')+1);
		    current_pop_start = 0;
		    r += "<ol>";
		} else if (t[0] == "begin_itemize") {
		    item_level += 1;
		    s = s.slice(s.indexOf('}')+1);
		    current_pop_start = 0;
		    r += "<ul>";
		}
	    }
	    t = itemenum_beginend_pop(s,current_pop_start);
	    while (level > 0 && t[0] != "") {
		t = itemenum_beginend_pop(s,current_pop_start);
		if (t[0].slice(0,4) == "item") {
		    if (level == 1) {
			if (counter == 0) {
			    r += s.slice(0,t[1]) + '<li>';
			    s = s.slice(t[1]+5);
                            current_pop_start = 0;
                            counter += 1;
			} else {
			    r += s.slice(0,t[1]) + '</li><li>';
			    s = s.slice(t[1]+5);
			    current_pop_start = 0;
                            counter += 1;
			}
		    }
		    if (level > 1) {
                        current_pop_start = t[1] + 1;
		    }
		}
		if (t[0].slice(0,4) == "begi") {
                    level += 1;
		    if (t[0] == "begin_enum_with_token") {
                        enum_level += 1;
		    } else if (t[0] == "begin_enum") {
			enum_level += 1;
		    } else if (t[0] == "begin_itemize") {
                        item_level += 1;
		    }
		    if (level == 2) {
                        level_two_start = t[1];
		    }
                    current_pop_start = t[1] + 1;
		}
		if (t[0].slice(0,4) == "end_") {
                    level -= 1;
		    if (t[0] == "end_enum") {
                        enum_level -= 1;
		    } else if (t[0] == "end_itemize") {
			item_level -= 1;
		    }
		    if (level == 1) {
			if (t[0] == 'end_enum') {
                            level_two_end = t[1] + 15;
			} else {
                            level_two_end = t[1] + 13;
			}
			r += s.slice(0,level_two_start);
			r += replace_enumitem(s.slice(level_two_start,level_two_end));
			s = s.slice(level_two_end);
                        current_pop_start = 0;
		    } else if (level == 0) {
			if (t[0] == 'end_enum') {
			    r += s.slice(0,t[1])+'</li></ol>';
			    s = s.slice(t[1]+15);
                            current_pop_start = 0;
                            counter = 0;
			} else if (t[0] == 'end_itemize') {
			    r += s.slice(0,t[1])+'</li></ul>';
			    s = s.slice(t[1]+13);
                            current_pop_start = 0;
                            counter = 0;
			} 
		    }
		    else if (level > 1) {
			current_pop_start = t[1]+1;
		    }
		}
	    }
	}
	return r+s.slice(0);
    } else {
        return s;
    }
    return s;
}
function replace_images(texcode,label,temp=false) {
    var repl = asyreplacementindexes(texcode);
    var newtexcode='';
    var tempdir = '';
    d = new Date();
    if (repl.length==0) {
	newtexcode += texcode;
    } else {
	newtexcode += texcode.slice(0,repl[0][0]);
	var i;
	var three;
	for (i=0; i < repl.length-1;i++) {
            three = '';
	    if (texcode.slice(repl[i][0],repl[i][1]).indexOf('import three') !==-1) {
		three = '+0_0';
	    }
	    newtexcode += '<img class=\"displayed\" src=\"/media/'+tempdir+label+'-'+(i+1).toString()+three+'.png'+"?"+d.getTime()+'\" alt=\"Please save to view image\"/>';
	    newtexcode += texcode.slice(repl[i][1],repl[i+1][0]);
	}
        three='';
	if (texcode.slice(repl[repl.length-1][0],repl[repl.length-1][1]).indexOf('import three') !== -1) {
	    three = '+0_0';
	}
	newtexcode += '<img class=\"displayed\" src=\"/media/'+tempdir+label+'-'+repl.length.toString()+three+'.png'+"?"+d.getTime()+'\" alt=\"Please save to view image\"/>';
	newtexcode += texcode.slice(repl[repl.length-1][1]);
    }
    var repl2 = tikzreplacementindexes(newtexcode);
    var new2texcode = '';
    if (repl2.length == 0) {
        new2texcode += newtexcode;
    }
    else {
	new2texcode += newtexcode.slice(0,repl2[0][0]);
	var i;
	for (i=0; i < repl2.length-1;i++) {
            new2texcode += '<img class=\"inline-displayed\" src=\"/media/'+tempdir+'tikz'+label+'-'+(i+1).toString()+'.png'+"?"+d.getTime()+'\" alt=\"Please save to view image\"/>';
	    new2texcode += newtexcode.slice(repl2[i][1],repl2[i+1][0]);
	}
	new2texcode+='<img class=\"inline-displayed\" src=\"/media/'+tempdir+'tikz'+label+'-'+repl2.length.toString()+'.png'+"?"+d.getTime()+'\" alt=\"Please save to view image\"/>';
	new2texcode += texcode.slice(repl2[repl2.length-1][1]);
    }
    return new2texcode;
}

function replace_center(s) {
    s = s.replace(/\\begin{center}/g,'<p style="text-align:center;\">');
    s = s.replace(/\\end{center}/g,'</p>\n');
    return s;
}