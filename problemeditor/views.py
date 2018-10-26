from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404,JsonResponse
from django.utils.http import urlquote,urlunquote
from django.template import loader,RequestContext
from django.template.loader import get_template,render_to_string
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.contrib.admin.models import LogEntry, ADDITION,CHANGE,DELETION
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.views.generic import UpdateView,CreateView,DeleteView,ListView,DetailView

from formtools.wizard.views import SessionWizardView

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Comment,QuestionType,ProblemApproval,TestCollection,NewTag,Round,UserType,Source,SourceType,BookChapter
from .forms import SolutionForm,CommentForm,ApprovalForm,AddContestForm,DuplicateProblemForm
from .forms import UploadContestForm,HTMLLatexForm
from .forms import NewTagForm,AddNewTagForm,EditMCAnswer,EditSAAnswer,MCProblemTextForm,SAProblemTextForm,ChangeQuestionTypeForm1,ChangeQuestionTypeForm2MC,ChangeQuestionTypeForm2MCSA,ChangeQuestionTypeForm2SA,ChangeQuestionTypeForm2PF,DifficultyForm,NewTypeForm,NewRoundForm,NewBookSourceForm,NewContestSourceForm,NewPersonSourceForm,NewChapterForm,NewProblemPFForm,NewProblemMCForm,NewProblemSAForm
from randomtest.utils import goodtag,goodurl,newtexcode,newsoltexcode,compileasy,compiletikz,sorted_nicely

from django.db.models import Count

from django import forms

from bs4 import BeautifulSoup
import bs4
from itertools import chain

def show_mc_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type')==QuestionType.objects.get(question_type='multiple choice')

def show_sa_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type')==QuestionType.objects.get(question_type='short answer')

def show_pf_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type')==QuestionType.objects.get(question_type='proof')

def show_mcsa_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type')==QuestionType.objects.get(question_type='multiple choice short answer')

def show_mc_form_condition2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type_new')==QuestionType.objects.get(question_type='multiple choice')

def show_sa_form_condition2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type_new')==QuestionType.objects.get(question_type='short answer')

def show_pf_form_condition2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type_new')==QuestionType.objects.get(question_type='proof')

def show_mcsa_form_condition2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type_new')==QuestionType.objects.get(question_type='multiple choice short answer')

class AddProblemWizard(SessionWizardView):
    template_name='problemeditor/addviewwizard.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddProblemWizard, self).get_context_data(**kwargs)
        ctx['ctx'] = ctx
        ctx['nbar']= 'problemeditor'
        if self.storage.current_step=='5':
            qt=QuestionType.objects.get(pk=self.storage.get_step_data('0').get('0-question_type')) 
            if qt.question_type=='multiple choice':
                ctx['mc']=True
            if qt.question_type=='short answer':
                ctx['sa']=True
            if qt.question_type=='proof':
                ctx['pf']=True
            if qt.question_type=='multiple choice short answer':
                ctx['mcsa']=True
        if 'problem_text' in self.get_form_initial('1'):
            ctx['problem_text']=self.get_form_initial('1')['problem_text']
        if 'mc_problem_text' in self.get_form_initial('1'):
            ctx['mc_problem_text']=self.get_form_initial('1')['mc_problem_text']
        return ctx
    def get_form_initial(self, step):
        # steps are named 'step1', 'step2', 'step3'
        current_step = self.storage.current_step
        
        # get the data for step 1 on step 3
        if current_step == '5':#CHANGE THIS
            init_data = self.storage.get_step_data('0')
            qtype = init_data.get('0-question_type')
            q=QuestionType.objects.get(pk=qtype)
            if q.question_type=='multiple choice':
                prev_data = self.storage.get_step_data('1')
                some_var = prev_data.get('1-mc_problem_text','')+'\n\n'+'$\\textbf{(A) }'+prev_data.get('1-answer_A','')+'\\qquad \\textbf{(B) }'+prev_data.get('1-answer_B','')+'\\qquad \\textbf{(C) }'+prev_data.get('1-answer_C','')+'\\qquad \\textbf{(D) }'+prev_data.get('1-answer_D','')+'\\qquad \\textbf{(E) }'+prev_data.get('1-answer_E','')+'$\n\n'
                return self.initial_dict.get(step, {'mc_problem_text': some_var})
            elif q.question_type=='short answer':
                prev_data = self.storage.get_step_data('2')
                some_var = prev_data.get('2-problem_text','')
                return self.initial_dict.get(step, {'problem_text': some_var})
            elif q.question_type=='proof':
                prev_data = self.storage.get_step_data('3')
                some_var = prev_data.get('3-problem_text','')
                return self.initial_dict.get(step, {'problem_text': some_var})
            elif q.question_type=='multiple choice short answer':
                prev_data = self.storage.get_step_data('4')
                some_var = prev_data.get('4-mc_problem_text','')
                some_var1 = prev_data.get('4-problem_text','')
                return self.initial_dict.get(step, {'mc_problem_text': some_var,'problem_text': some_var1})
        return self.initial_dict.get(step, {})
    def done(self,form_list,**kwargs):
        D = {}
        for form in form_list:
            x = form.cleaned_data
            for i in x:
                D[i] = x[i]
        if D['question_type'].question_type == 'short answer':
            prob = Problem(
                problem_text = D['problem_text'],
                author_name = D['author_name'],
                answer = D['correct_short_answer_answer'],
                sa_answer = D['correct_short_answer_answer'],
                type_new = D['type'],
                question_type_new = D['question_type'],
                )
        elif D['question_type'].question_type == 'proof':
            prob = Problem(
                problem_text = D['problem_text'],
                author_name = D['author_name'],
                type_new = D['type'],
                question_type_new = D['question_type'],
                )
        elif D['question_type'].question_type == 'multiple choice':
            prob = Problem(
                mc_problem_text = D['mc_problem_text'],
                author_name = D['author_name'],
                answer = D['correct_multiple_choice_answer'],
                mc_answer = D['correct_multiple_choice_answer'],
                answer_choices = '$\\textbf{(A) }'+D['answer_A']+'\\qquad\\textbf{(B) }'+D['answer_B']+'\\qquad\\textbf{(C) }'+D['answer_C']+'\\qquad\\textbf{(D) }'+D['answer_D']+'\\qquad\\textbf{(E) }'+D['answer_E']+'$',
                answer_A = D['answer_A'],
                answer_B = D['answer_B'],
                answer_C = D['answer_C'],
                answer_D = D['answer_D'],
                answer_E = D['answer_E'],
                type_new = D['type'],
                question_type_new = D['question_type'],
                )
        elif D['question_type'].question_type == 'multiple choice short answer':
            prob = Problem(
                problem_text = D['problem_text'],
                mc_problem_text = D['mc_problem_text'],
                author_name = D['author_name'],
                answer = D['correct_multiple_choice_answer'],
                mc_answer = D['correct_multiple_choice_answer'],
                answer_choices = '$\\textbf{(A) }'+D['answer_A']+'\\qquad\\textbf{(B) }'+D['answer_B']+'\\qquad\\textbf{(C) }'+D['answer_C']+'\\qquad\\textbf{(D) }'+D['answer_D']+'\\qquad\\textbf{(E) }'+D['answer_E']+'$',
                answer_A = D['answer_A'],
                answer_B = D['answer_B'],
                answer_C = D['answer_C'],
                answer_D = D['answer_D'],
                answer_E = D['answer_E'],
                type_new = D['type'],
                question_type_new = D['question_type'],
                )
        prob.save()
        prob.question_type.add(D['question_type'])
        prob.types.add(D['type'])
        prob.author = self.request.user
        t = prob.type_new
        t.top_index += 1
        t.save()
        prob.label = t.type+str(t.top_index)
        prob.readable_label = t.label+' '+str(t.top_index)
        prob.top_solution_number = 1
        prob.save()

        compileasy(prob.mc_problem_text,prob.label)
        compileasy(prob.problem_text,prob.label)
        compiletikz(prob.mc_problem_text,prob.label)
        compiletikz(prob.problem_text,prob.label)


        prob.display_problem_text=newtexcode(prob.problem_text,prob.label,'')
        prob.display_mc_problem_text=newtexcode(prob.mc_problem_text,prob.label,prob.answers())

        sol = Solution(solution_text = D['solution_text'],parent_problem = prob)
        sol.save()
        sol.solution_number = 1
        sol.authors.add(self.request.user)
        sol.problem_label = prob.label
        sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
        sol.save()
        prob.solutions.add(sol)
        prob.save()
        compileasy(sol.solution_text,prob.label,sol = "sol1")
        compiletikz(sol.solution_text,prob.label,sol = "sol1")
        LogEntry.objects.log_action(
            user_id = self.request.user.id,
            content_type_id = ContentType.objects.get_for_model(prob).pk,
            object_id = prob.id,
            object_repr = prob.label,
            action_flag = ADDITION,
            change_message = "problemeditor/CM/bytopic/"+prob.type_new.type+'/'+str(prob.pk)+'/',
            )
        return redirectproblem(self.request,prob.pk)
#        return redirect('/problemeditor/detailedview/'+str(prob.pk)+'/')


# Create your views here.
@login_required
def typeview(request):
    userprofile,boolcreated = UserProfile.objects.get_or_create(user=request.user)
    allowed_types = list(userprofile.user_type_new.allowed_types.all())
    allowed_types = sorted(allowed_types,key=lambda x:(-x.is_contest,x.label))
    rows = []
    for i in allowed_types:
        P = i.problems.all()
        num_problems = P.count()
        num_untagged = P.filter(newtags__isnull = True).count()#
        num_nosolutions = P.filter(solutions__isnull = True).count()
        rows.append((i,num_untagged,num_nosolutions))
    template = loader.get_template('problemeditor/typeview.html')
    context = {'rows': rows, 'nbar': 'problemeditor'}
    return HttpResponse(template.render(context,request))

@login_required
def sourceview(request):
    books = SourceType.objects.get(name="book").source_set.all()
    contests = SourceType.objects.get(name="contest").source_set.all()
    people = SourceType.objects.get(name="person").source_set.all()
    book_rows = []
    contest_rows = []
    person_rows = []
    for b in books:
        P = b.problem_set.all()
        num_problems = P.count()
        num_untagged = P.filter(newtags__isnull = True).count()#
        num_nosolutions = P.filter(solutions__isnull = True).count()
        book_rows.append((b,num_untagged,num_nosolutions,num_problems))
    for c in contests:
        P = c.problem_set.all()
        num_problems = P.count()
        num_untagged = P.filter(newtags__isnull = True).count()#
        num_nosolutions = P.filter(solutions__isnull = True).count()
        contest_rows.append((c,num_untagged,num_nosolutions,num_problems))
    for p in people:
        P = p.problem_set.all()
        num_problems = P.count()
        num_untagged = P.filter(newtags__isnull = True).count()#
        num_nosolutions = P.filter(solutions__isnull = True).count()
        person_rows.append((p,num_untagged,num_nosolutions,num_problems))
    context = {}
    context['book_rows'] = book_rows
    context['contest_rows'] = contest_rows
    context['person_rows'] = person_rows
    context['nbar'] = 'problemeditor'
    return render(request, 'problemeditor/sourceview.html',context)

@user_passes_test(lambda u: mod_permission(u))
def load_new_book(request,**kwargs):
    form = NewBookSourceForm()
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-source.html',{'form':form,'source_type':'book'})})

@user_passes_test(lambda u: mod_permission(u))
def load_new_contest(request,**kwargs):
    form = NewContestSourceForm()
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-source.html',{'form':form,'source_type':'contest'})})

@user_passes_test(lambda u: mod_permission(u))
def load_new_person(request,**kwargs):
    form = NewPersonSourceForm()
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-source.html',{'form':form,'source_type':'person'})})

@user_passes_test(lambda u: mod_permission(u))
def save_source(request,**kwargs):
    st_name = request.POST.get('source_type','')
    source_type =  get_object_or_404(SourceType,name = st_name)
    if st_name == 'book':
        form = NewBookSourceForm(request.POST)
        form.save()
        form.instance.source_type = source_type
        form.instance.save()
        return JsonResponse({'st':st_name,'source-row':render_to_string('problemeditor/source-row.html',{'source_type':st_name,'source':form.instance,'untag':0,'unsolution':0,'num':0})})
    elif st_name == 'contest':
        form = NewContestSourceForm(request.POST)
        form.save()
        form.instance.source_type = source_type
        form.instance.save()
        return JsonResponse({'st':st_name,'source-row':render_to_string('problemeditor/source-row.html',{'source_type':st_name,'source':form.instance,'untag':0,'unsolution':0,'num':0})})
    elif st_name == 'person':
        form = NewPersonSourceForm(request.POST)
        form.save()
        form.instance.source_type = source_type
        form.instance.save()
        return JsonResponse({'st':st_name,'source-row':render_to_string('problemeditor/source-row.html',{'source_type':st_name,'source':form.instance,'untag':0,'unsolution':0,'num':0})})

@login_required
def bookview(request,pk):
    book = get_object_or_404(Source, pk=pk)
    if book.source_type.name != "book":
        raise Http404("Incorrect source type")
    book_chapters = book.bookchapter_set.all()
#    num_untagged = book_problems.filter(newtags__isnull = True).count()
    rows = []
    for chap in book_chapters:
        chapter_problems = chap.problem_set.all()
        rows.append((chap, 'Chapter '+str(chap.chapter_number)+': '+chap.name,chapter_problems.filter(newtags__isnull = True).count(),chapter_problems.filter(solutions__isnull = True).count(),chapter_problems.count()))
    context = {}
    context['book'] = book
    context['nbar'] = 'problemeditor'
    context['rows'] = rows
    return render(request,'problemeditor/bookview.html',context)

@user_passes_test(lambda u: mod_permission(u))
def load_new_chapter(request,**kwargs):
    form = NewChapterForm()
    book_pk = request.GET.get('pk')
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-chapter.html',{'form':form,'book_pk':book_pk})})

@user_passes_test(lambda u: mod_permission(u))
def save_chapter(request,**kwargs):
    book_pk = request.POST.get('book_pk','')
    book =  get_object_or_404(Source,pk = book_pk)
    form = NewChapterForm(request.POST)
    form.save()
    form.instance.source = book
    form.instance.save()
    return JsonResponse({'chapter-row':render_to_string('problemeditor/book-chapter-row.html',{'chapter':form.instance,'chapter_label': "Chapter "+str(form.instance.chapter_number)+": "+form.instance.name,'untag':0,'unsolution':0,'num':0}),'chapter-number':form.instance.chapter_number})

@user_passes_test(lambda u: mod_permission(u))
def chapterview(request,book_pk,chapter_pk):
    book = get_object_or_404(Source, pk = book_pk)
    if book.source_type.name != "book":
        raise Http404("Incorrect source type")
#        problems = list(Problem.objects.filter(test_label=testlabel))
    chapter = get_object_or_404(BookChapter, pk = chapter_pk)
    problems = chapter.problem_set.all()
#    problems = sorted(problems, key=lambda x:(x.year,x.problem_number))

    paginator=Paginator(problems,150)
    page = request.GET.get('page')
    try:
        prows=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    userprofile = request.user.userprofile#
    owned_groups = userprofile.problem_groups.all()#
    editable_groups = userprofile.editable_problem_groups.all()#
    probgroups = list(chain(owned_groups,editable_groups))#

    template = loader.get_template('problemeditor/typetagview.html')
    context = {
        'rows' : prows,
        'nbar': 'problemeditor',
#        'type':typ.type,
        'typelabel': 'Sourced Problems',
        'tag':'Chapter '+str(chapter.chapter_number)+': '+chapter.name,
        'tags':NewTag.objects.exclude(tag='root'),
        'is_sourced':1,
        'is_chapter':1,
        'source':book,
        'probgroups': probgroups,
        }
    return HttpResponse(template.render(context,request))

@user_passes_test(lambda u: mod_permission(u))
def load_addproblemform(request,**kwargs):
    st = request.GET.get('st')
    print('st1',st)
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-problem.html',{'source_type' : st})})

@user_passes_test(lambda u: mod_permission(u))
def load_qt_addproblemform(request,**kwargs):
    qt = request.GET.get('qt','')
    st = request.GET.get('st','')
    print('st',st)
    if qt == 'sa':
        form = NewProblemSAForm(st=st)
    if qt == 'mc':
        form = NewProblemMCForm(st=st)
    if qt == 'pf':
        form = NewProblemPFForm(st=st)
    return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))

@user_passes_test(lambda u: mod_permission(u))
def add_sourced_problem(request,**kwargs):
#depends on book, person, or contest....
    userprofile = request.user.userprofile
    is_chapter = 0
    is_contest = 0
    tags = NewTag.objects.exclude(tag='root')
    st = request.POST.get('st','')
    if 'book_pk' in kwargs:
        source = get_object_or_404(Source,pk = kwargs['book_pk'])
    if 'chapter_pk' in kwargs:
        chapter = get_object_or_404(BookChapter,pk = kwargs['chapter_pk'])
        is_chapter = 1
    if 'person_pk' in kwargs:
        source = get_object_or_404(Source,pk = kwargs['person_pk'])
    if 'contest_pk' in kwargs:
        source = get_object_or_404(Source,pk = kwargs['contest_pk'])
        is_contest = 1
    if request.method == "POST":
        form = request.POST
        qt = form.get('question-type','')
        typ = Type.objects.get(label = "Sourced")
        question_type = QuestionType.objects.get(question_type = qt)
        if qt == "multiple choice":
            pform = NewProblemMCForm(request.POST,st = st)

            if pform.is_valid():
                if is_contest:
                    if source.problem_set.filter(problem_number = int(pform.cleaned_data['problem_number'])).exists():
                        return JsonResponse({'error':'Problem with number already exists'})
                prob = pform.save()
                prob.type_new = typ
                prob.types.add(typ)
#####problem_number....
                if is_contest == 1:
                    prob.label = str(source.year) + source.contest_short_name + str(prob.problem_number)
                    prob.readable_label = str(source.year) + ' ' + source.contest_name + ' #' + str(prob.problem_number)
                else:
                    prob.label = 'Problem' + str(prob.pk)
                    prob.readable_label = 'Problem ' + str(prob.pk)
#####
                prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
                prob.mc_problem_text = prob.problem_text
                prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,prob.answers())
                compileasy(prob.mc_problem_text,prob.label)
                compileasy(prob.problem_text,prob.label)
                compiletikz(prob.mc_problem_text,prob.label)
                compiletikz(prob.problem_text,prob.label)
                prob.question_type_new = question_type
                prob.question_type.add(question_type)
                prob.author = request.user
                prob.answer_choices = prob.answers()
                prob.answer = prob.mc_answer
                prob.top_solution_number = 0
                try:
                    prob.year = int(source.year)###maybe bad
                except ValueError:
                    prob.year = 0
                prob.source = source
                if is_chapter == 1:
                    prob.book_chapter = chapter
                    forcount = chapter.problem_set.count() + 1
                else:
                    forcount = source.problem_set.count() + 1
                prob.save()
#problem_number
                return JsonResponse({'list-item':render_to_string('problemeditor/problem-snippets/paginated-list-item.html',{'prob':prob,'forcount':forcount,'tags':tags,'request':request}),'pk':prob.pk})#####only works for chapter
        elif qt == "short answer":
            pform = NewProblemSAForm(request.POST,st=st)
            if pform.is_valid():
                if is_contest:
                    if source.problem_set.filter(problem_number = int(pform.cleaned_data['problem_number'])).exists():
                        return JsonResponse({'error':'Problem with number already exists'})
                prob = pform.save()
                prob.type_new = typ
                prob.types.add(typ)
                if is_contest == 1:
                    prob.label = str(source.year) + source.contest_short_name + str(prob.problem_number)
                    prob.readable_label = str(source.year) + ' ' + source.contest_name + ' #' + str(prob.problem_number)
                else:
                    prob.label = 'Problem' + str(prob.pk)
                    prob.readable_label = 'Problem ' + str(prob.pk)
                prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
                prob.mc_problem_text = prob.problem_text
                prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,'')
                compileasy(prob.mc_problem_text,prob.label)
                compileasy(prob.problem_text,prob.label)
                compiletikz(prob.mc_problem_text,prob.label)
                compiletikz(prob.problem_text,prob.label)
                prob.question_type_new = question_type
                prob.question_type.add(question_type)
                prob.author = request.user
                prob.answer_choices = ''
                prob.answer = prob.sa_answer
                prob.top_solution_number = 0
                try:
                    prob.year = int(source.year)###maybe bad
                except ValueError:
                    prob.year = 0
                prob.source = source
                if is_chapter == 1:
                    prob.book_chapter = chapter
                    forcount = chapter.problem_set.count() + 1
                else:
                    forcount = source.problem_set.count() + 1
                prob.save()
#problem_number
                return JsonResponse({'list-item':render_to_string('problemeditor/problem-snippets/paginated-list-item.html',{'prob':prob,'forcount':forcount,'tags':tags,'request':request}),'pk':prob.pk})#####only works for chapter
        elif qt == "proof":
            pform = NewProblemPFForm(request.POST,st=st)
            if pform.is_valid():
                if is_contest:
                    if source.problem_set.filter(problem_number = int(pform.cleaned_data['problem_number'])).exists():
                        return JsonResponse({'error':'Problem with number already exists'})
                prob = pform.save()
                prob.type_new = typ
                prob.types.add(typ)
                if is_contest == 1:
                    prob.label = str(source.year)+source.contest_short_name + str(prob.problem_number)
                    prob.readable_label = str(source.year) + ' ' + source.contest_name + ' #' + str(prob.problem_number)
                else:
                    prob.label = 'Problem' + str(prob.pk)
                    prob.readable_label = 'Problem ' + str(prob.pk)
                prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
                prob.mc_problem_text = prob.problem_text
                prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,'')
                compileasy(prob.mc_problem_text,prob.label)
                compileasy(prob.problem_text,prob.label)
                compiletikz(prob.mc_problem_text,prob.label)
                compiletikz(prob.problem_text,prob.label)
                prob.question_type_new = question_type
                prob.question_type.add(question_type)
                prob.author = request.user
#                prob.answer_choices = prob.answers()
                prob.answer = ''
                prob.top_solution_number = 0
                try:
                    prob.year = int(source.year)###maybe bad
                except ValueError:
                    prob.year = 0
                prob.source = source
                if is_chapter == 1:
                    prob.book_chapter = chapter
                    forcount = chapter.problem_set.count() + 1
                else:
                    forcount = source.problem_set.count() + 1
                prob.save()
#problem_number
                return JsonResponse({'list-item':render_to_string('problemeditor/problem-snippets/paginated-list-item.html',{'prob':prob,'forcount':forcount,'tags':tags,'request':request}),'pk':prob.pk})#####only works for chapter

@user_passes_test(lambda u: mod_permission(u))
def personview(request,person_pk):
#check to make sure correct source type
    person = get_object_or_404(Source, pk = person_pk)
    if person.source_type.name != "person":
        raise Http404("Incorrect source type")
    problems = person.problem_set.all()

    paginator=Paginator(problems,150)
    page = request.GET.get('page')
    try:
        prows=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    userprofile = request.user.userprofile#
    owned_groups = userprofile.problem_groups.all()#
    editable_groups = userprofile.editable_problem_groups.all()#
    probgroups = list(chain(owned_groups,editable_groups))#


    template = loader.get_template('problemeditor/typetagview.html')
    context = {
        'rows' : prows,
        'nbar': 'problemeditor',
#        'type':typ.type,
        'typelabel': 'Sourced Problems',
        'tag':'Person: '+person.author,
        'tags':NewTag.objects.exclude(tag='root'),
        'is_sourced':1,
#        'is_chapter':1,
        'source':person,
        'probgroups':probgroups,
        }
    return HttpResponse(template.render(context,request))

@user_passes_test(lambda u: mod_permission(u))
def contestview(request,contest_pk):
    contest = get_object_or_404(Source, pk = contest_pk)
    if contest.source_type.name != "contest":
        raise Http404("Incorrect source type")
    problems = contest.problem_set.order_by('problem_number')

    paginator = Paginator(problems,150)
    page = request.GET.get('page')
    try:
        prows = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    userprofile = request.user.userprofile#
    owned_groups = userprofile.problem_groups.all()#
    editable_groups = userprofile.editable_problem_groups.all()#
    probgroups = list(chain(owned_groups,editable_groups))#

    template = loader.get_template('problemeditor/typetagview.html')
    context = {
        'rows' : prows,
        'nbar' : 'problemeditor',
#        'type':typ.type,
        'typelabel' : 'Sourced Problems',
        'tag' : 'Contest: '+str(contest),
        'tags' : NewTag.objects.exclude(tag='root'),
        'is_sourced' : 1,
#        'is_chapter':1,
        'source' : contest,
        'probgroups':probgroups,
        }
    return HttpResponse(template.render(context,request))


@login_required
def tagview(request,type):
    typ = get_object_or_404(Type, type = type)
    newtags = NewTag.objects.all().exclude(label = 'root').order_by('tag')
    rows = []
    probsoftype = Problem.objects.filter(type_new = typ)
    untagged = probsoftype.filter(newtags__isnull = True)
    num_untagged = untagged.count()
    for tag in newtags:#i
        T = tag.problems.filter(type_new = typ)#probsoftype.filter(newtags__in=[tag])
        num_problems = T.count()
        num_nosolutions = T.filter(solutions__isnull=True).count()
        if num_problems > 0:
            rows.append((goodurl(str(tag)),tag,num_nosolutions,num_problems))

    root_tag = NewTag.objects.get(label='root')
    rows1 = []
    for c1 in root_tag.children.all():
        T_startswith = probsoftype.filter(newtags__in = NewTag.objects.filter(tag__startswith = c1.tag))
        T = c1.problems.filter(type_new = typ)
        num_probs_sw = T_startswith.count()
        num_nosolutions_sw = T_startswith.filter(solutions__isnull = True).count()
        num_probs = T.count()
        num_nosolutions = T.filter(solutions__isnull = True).count()
        if num_probs_sw > 0:
            rows2 = []
            for c2 in c1.children.all():
                T_startswith2 = probsoftype.filter(newtags__in = NewTag.objects.filter(tag__startswith = c2.tag))
                T2 = c2.problems.filter(type_new = typ)
                num_probs_sw2 = T_startswith2.count()
                num_nosolutions_sw2 = T_startswith2.filter(solutions__isnull = True).count()
                num_probs2 = T2.count()
                num_nosolutions2 = T2.filter(solutions__isnull = True).count()
                if num_probs_sw2 > 0:
                    rows3 = []
                    for c3 in c2.children.all():
                        T3 = c3.problems.filter(type_new = typ)
                        num_probs3 = T3.count()
                        num_nosolutions3 = T3.filter(solutions__isnull = True).count()
                        if num_probs3 > 0:
                            rows3.append((goodurl(str(c3)),c3,num_nosolutions3,num_probs3))
                    rows2.append((rows3,goodurl(str(c2)),c2,num_nosolutions_sw2,num_probs_sw2,num_nosolutions2,num_probs2))
            rows1.append((rows2,goodurl(str(c1)),c1,num_nosolutions_sw,num_probs_sw,num_nosolutions,num_probs))
    
    template=loader.get_template('problemeditor/tagview.html')
    context= {'rows': rows, 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','prefix':'bytag','rows1' : rows1}
    return HttpResponse(template.render(context,request))

@login_required
def testview(request,type):
    typ = get_object_or_404(Type, type = type)
    probsoftype = Problem.objects.filter(type_new = typ)
    num_untagged = probsoftype.filter(newtags__isnull = True).count()
    testlabels = []
    pot = list(probsoftype)
    for i in range(0,len(pot)):
        testlabels.append(pot[i].test_label)
    testlabels = sorted_nicely(set(testlabels))
    rows2 = []
    for i in range(0,len(testlabels)):
        rows2.append((testlabels[i],probsoftype.filter(test_label = testlabels[i]).filter(newtags__isnull = True).count(),probsoftype.filter(test_label = testlabels[i]).filter(solutions__isnull = True).count(),probsoftype.filter(test_label = testlabels[i]).count()))
        
    userprofile = request.user.userprofile#
    owned_groups = userprofile.problem_groups.all()#
    editable_groups = userprofile.editable_problem_groups.all()#
    probgroups = list(chain(owned_groups,editable_groups))#

    template = loader.get_template('problemeditor/testview.html')
    context = { 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','rows2':rows2,'prefix':'bytest', 'probgroups' : probgroups}
    return HttpResponse(template.render(context,request))


@login_required
def typetagview(request,type,pk):#type,tag):
    context = {}
    typ = get_object_or_404(Type, type = type)
    if pk == "untagged":
        problems = list(typ.problems.filter(newtags__isnull = True))
        tag = "untagged"
    else:
        tag = get_object_or_404(NewTag,pk=pk)#this is new. ISSUE: how to deal with untagged?
        if request.method =="GET" and request.GET.get('exact') == "true":
            problems = list(tag.problems.filter(type_new = typ))
            context['exacttag'] = 1
        else:
            problems = Problem.objects.filter(type_new = typ)
            problems = problems.filter(newtags__in=NewTag.objects.filter(tag__startswith=tag)).distinct()
    problems = sorted(problems, key = lambda x:(x.problem_number,x.year))

    template = loader.get_template('problemeditor/typetagview.html')

    paginator = Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    userprofile = request.user.userprofile#
    owned_groups = userprofile.problem_groups.all()#
    editable_groups = userprofile.editable_problem_groups.all()#
    probgroups = list(chain(owned_groups,editable_groups))#

    context['probgroups'] = probgroups
    context['rows'] = prows
    context['type'] = typ.type
    context['nbar'] = 'problemeditor'
    context['tag'] = tag#####
    context['typelabel'] = typ.label
    context['tags'] = NewTag.objects.exclude(tag = 'root')
    return HttpResponse(template.render(context,request))

@login_required
def CMtypetagview(request,type,tag):
    tag = goodtag(tag)
    typ = get_object_or_404(Type, type = type)
    rows = []
    if tag != 'untagged':
        ttag = get_object_or_404(NewTag, tag = tag)
        problems = list(ttag.problems.filter(type_new = typ))
    else:
        problems = list(typ.problems.filter(newtags__isnull = True))
    problems = sorted(problems, key=lambda x:x.pk)
    template = loader.get_template('problemeditor/CMtypetagview.html')

    paginator = Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    context= {'rows' : prows, 'type' : typ.type, 'nbar': 'problemeditor','tag':tag,'typelabel':typ.label}
    return HttpResponse(template.render(context,request))

@login_required
def testlabelview(request,type,testlabel):
    typ = get_object_or_404(Type, type=type)
    if testlabel != 'untagged':
        problems = list(Problem.objects.filter(test_label=testlabel))
    else:
        problems = typ.problems.filter(newtags__isnull=True)
    problems = sorted(problems, key=lambda x:(x.year,x.problem_number))

    paginator=Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)


    userprofile = request.user.userprofile#
    owned_groups = userprofile.problem_groups.all()#
    editable_groups = userprofile.editable_problem_groups.all()#
    probgroups = list(chain(owned_groups,editable_groups))#

    template = loader.get_template('problemeditor/typetagview.html')
    context = {
        'rows' : prows,
        'nbar': 'problemeditor',
        'type':typ.type,
        'typelabel':typ.label,
        'tag':testlabel,
        'tags':NewTag.objects.exclude(tag='root'),
        'probgroups':probgroups,
        }
    return HttpResponse(template.render(context,request))

@login_required
def CMtopicview(request,type):#unapprovedview
    typ=get_object_or_404(Type, type=type)
    rows=[]
    problems=list(typ.problems.all())
    problems=sorted(problems, key=lambda x:(x.pk))
    template=loader.get_template('problemeditor/CMtopicview.html')#unapproved

    paginator=Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    context= {'rows' : prows, 'type' : typ.type, 'nbar': 'problemeditor','typelabel':typ.label}
    return HttpResponse(template.render(context,request))

#####Check it
@login_required
def problemview(request,**kwargs):#,type,tag,label):
    userprofile = request.user.userprofile#
    owned_groups = userprofile.problem_groups.all()#
    editable_groups = userprofile.editable_problem_groups.all()#
    probgroups = list(chain(owned_groups,editable_groups))#

    context = {}
    context['nbar'] = 'problemeditor'
    context['tags'] = NewTag.objects.exclude(tag = 'root')
    context['probgroups'] = probgroups
    if 'type' in kwargs:
        type = kwargs['type']
        if 'tag' in kwargs:
            tag = kwargs['tag']
            tag = goodtag(tag)
        if 'label' in kwargs:
            label = kwargs['label']
        if 'pk' in kwargs:
            tag_object = get_object_or_404(NewTag,pk = kwargs['pk'])
            tag = tag_object.tag
        typ = get_object_or_404(Type, type = type)
        prob = get_object_or_404(Problem, label = label)
        context['rows'] = prob.solutions.all()
        context['prob'] = prob
        context['typelabel'] = typ.label
        context['label'] = label
        context['tag'] = tag
#        userprofile = request.user.userprofile
        return render(request, 'problemeditor/view.html', context)
    else:
        context['is_sourced'] = 1
        if 'chapter_pk' in kwargs and 'book_pk' in kwargs:
            context['is_chapter'] = 1
            chapter = get_object_or_404(BookChapter,pk = kwargs['chapter_pk'])
            book = get_object_or_404(Source,pk = kwargs['book_pk'])
#            context['chapter'] = chapter
            context['source'] = book
            prob = get_object_or_404(Problem,pk = kwargs['problem_pk'])
            context['prob'] = prob
            context['rows'] = prob.solutions.all()
            context['chapter_name'] = 'Chapter '+str(chapter.chapter_number)+': '+chapter.name
            return render(request, 'problemeditor/view.html', context)
        if 'contest_pk' in kwargs:
            contest = get_object_or_404(Source,pk = kwargs['contest_pk'])
            context['source'] = contest
            prob = get_object_or_404(Problem,pk = kwargs['problem_pk'])
            context['prob'] = prob
            context['rows'] = prob.solutions.all()
            context['tag'] = 'Contest: '+str(contest)
            return render(request, 'problemeditor/view.html', context)
        if 'person_pk' in kwargs:
            person = get_object_or_404(Source,pk = kwargs['contest_pk'])
            context['source'] = person
            prob = get_object_or_404(Problem,pk = kwargs['problem_pk'])
            context['prob'] = prob
            context['rows'] = prob.solutions.all()
            context['tag'] = 'Person: '+str(person)
            return render(request, 'problemeditor/view.html', context)


class SolutionDeleteView(DeleteView):
    model = Solution
    template_name = 'problemeditor/solution_delete_form.html'
    success_url = "../../"

    def dispatch(self, *args, **kwargs):
        self.sol_id = kwargs['spk']
        if 'label' in kwargs:
            self.label = kwargs['label']
        if 'pk' in kwargs:
            self.pk = kwargs['pk']
        return super(SolutionDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Solution, pk=self.sol_id)
    def get_context_data(self, *args, **kwargs):
        context = super(SolutionDeleteView,self).get_context_data(*args,**kwargs)
        try:
            context['prob'] = get_object_or_404(Problem,label=self.label)
        except AttributeError:
            context['prob'] = get_object_or_404(Problem,pk=self.pk)
        context['solution'] = get_object_or_404(Solution, pk=self.sol_id)
        return context


@login_required
def untaggedview(request,type):
    typ=get_object_or_404(Type, type=type)
    rows=[]
    problems=list(Problem.objects.filter(type_new=typ).filter(newtags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))

    userprofile = request.user.userprofile#
    owned_groups = userprofile.problem_groups.all()#
    editable_groups = userprofile.editable_problem_groups.all()#
    probgroups = list(chain(owned_groups,editable_groups))#

    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : problems, 'type' : typ.type, 'nbar': 'problemeditor','probgroups':probgroups}
    return HttpResponse(template.render(context,request))

@login_required
def detailedproblemview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    context={}
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../',typ.label),('../',goodtag(kwargs['tag'])),]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../',typ.label+' Problems'),]
    else:
        breadcrumbs=[]
    context['prob'] = prob
    context['nbar'] = 'problemeditor'
    context['breadcrumbs'] = breadcrumbs
    context['tags'] = NewTag.objects.exclude(tag='root')
    return render(request, 'problemeditor/detailedview.html', context)


@user_passes_test(lambda u: mod_permission(u))
def addcontestview(request,type,num):
    typ=get_object_or_404(Type, type=type)
    num=int(num)
    sa = QuestionType.objects.get(question_type='short answer')
    mc = QuestionType.objects.get(question_type='multiple choice')
    pf = QuestionType.objects.get(question_type='proof')
    if request.method == "POST":
        form=request.POST
        F=form#.cleaned_data
        formletter = ''
        if 'formletter' in F:
            formletter = F['formletter']
        year = F['year']
        if 'round' in F:
            round = get_object_or_404(Round, pk=F['round'])
            readablelabel = F['year'] + ' ' + round.readable_label_pre_form + formletter
            default_question_type = round.default_question_type
            readablelabel = readablelabel.rstrip()
            post_label = round.readable_label_post_form
            label = F['year'] + round.name.replace(' ','') + formletter#####no spaces
        else:
            readablelabel = F['year'] + ' ' + typ.readable_label_pre_form + formletter
            default_question_type = typ.default_question_type
            readablelabel = readablelabel.rstrip()
            post_label = typ.readable_label_post_form
            label = F['year'] + type + formletter#####
        if default_question_type=='mc':
            for i in range(1,num+1):
                p=Problem(mc_problem_text = F['problem_text'+str(i)],
                          problem_text = F['problem_text'+str(i)],
                          answer = F['answer'+str(i)],
                          mc_answer = F['answer'+str(i)],
                          answer_choices = '$\\textbf{(A) }'+F['answer_A'+str(i)]+'\\qquad\\textbf{(B) }'+F['answer_B'+str(i)]+'\\qquad\\textbf{(C) }'+F['answer_C'+str(i)]+'\\qquad\\textbf{(D) }'+F['answer_D'+str(i)]+'\\qquad\\textbf{(E) }'+F['answer_E'+str(i)]+'$',
                          answer_A = F['answer_A'+str(i)],
                          answer_B = F['answer_B'+str(i)],
                          answer_C = F['answer_C'+str(i)],
                          answer_D = F['answer_D'+str(i)],
                          answer_E = F['answer_E'+str(i)],
                          label = label+str(i),
                          readable_label = readablelabel+post_label+str(i),
                          type_new = typ,
                          question_type_new = mc,
                          problem_number = i,
                          year = F['year'],
                          form_letter = formletter,
                          test_label = label,
                          top_solution_number = 0,
                          )
                p.save()
                if 'round' in F:
                    p.round = round
                p.types.add(typ)
                p.question_type.add(mc)
                p.save()
                compileasy(p.mc_problem_text,p.label)
                compileasy(p.problem_text,p.label)
                compiletikz(p.mc_problem_text,p.label)
                compiletikz(p.problem_text,p.label)
                p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                p.save()
        if default_question_type == 'sa':
            for i in range(1,num + 1):
                p = Problem(problem_text = F['problem_text' + str(i)],
                          answer = F['answer' + str(i)],
                          sa_answer = F['answer' + str(i)],
                          label = label + str(i),
                          readable_label = readablelabel + post_label + str(i),
                          type_new = typ,
                          question_type_new = sa,
                          problem_number = i,
                          year = F['year'],
                          form_letter = formletter,
                          test_label = label,
                          top_solution_number = 0,
                          )
                p.save()
                if 'round' in F:
                    p.round = round
                p.types.add(typ)
                p.question_type.add(sa)
                p.save()
                compileasy(p.mc_problem_text,p.label)
                compileasy(p.problem_text,p.label)
                compiletikz(p.mc_problem_text,p.label)
                compiletikz(p.problem_text,p.label)
                p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                p.save()
        if default_question_type=='pf':
            for i in range(1,num+1):
                p=Problem(problem_text=F['problem_text'+str(i)],
                          label = label+str(i),
                          readable_label = readablelabel + post_label + str(i),
                          type_new = typ,
                          question_type_new = pf,
                          problem_number = i,
                          year = F['year'],
                          form_letter = formletter,
                          test_label = label,
                          top_solution_number = 0,
                          )
                p.save()
                if 'round' in F:
                    p.round = round
                p.types.add(typ)
                p.question_type.add(pf)
                p.save()
                compileasy(p.mc_problem_text,p.label)
                compileasy(p.problem_text,p.label)
                compiletikz(p.mc_problem_text,p.label)
                compiletikz(p.problem_text,p.label)
                p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                p.save()
        P = Problem.objects.filter(test_label=label)
        if len(P)>0:
            t=Test(name=readablelabel)
#            if 'round' in F:
#                t=Test(name = F['year']+round.name)
#            readablelabel = F['year'] + ' ' + round.readable_label_pre_form + formletter
#            else:
#                t=Test(name = readablelabel)# would this change for rounds
            t.save()
        for i in P:
            t.problems.add(i)
        t.types.add(typ)
        t.save()
        tc,boolcreated=TestCollection.objects.get_or_create(name=typ.label)
        tc.tests.add(t)
        tc.save()
        return redirect('/problemeditor/')
    form=AddContestForm(request.POST or None,num_probs=num,type=type)
    context={'nbar': 'problemeditor','num': num,'typ':typ,'nums':[i for i in range(1,num+1)]}
    if typ.default_question_type=='mc':
        context['mc']=True
    elif typ.default_question_type=='sa':
        context['sa']=True
    elif typ.default_question_type=='mcsa':
        context['mc']=True
        context['sa']=True
    else:
        context['pf']=True
    context['form']=form
    return render(request, 'problemeditor/addcontestform.html', context=context)


@login_required
def my_activity(request):
    log = LogEntry.objects.filter(user_id = request.user.id).filter(change_message__contains="problemeditor")
    linkedlog=[]
    for i in log:
        if i.content_type.name=='problem':
            if Problem.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))
        if i.content_type.name=='solution':
            if Solution.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))
        if i.content_type.name=='problem approval':
            if ProblemApproval.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))
    paginator=Paginator(linkedlog,50)
    page = request.GET.get('page')
    try:
        plog=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        plog = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        plog = paginator.page(paginator.num_pages)
    return render(request,'problemeditor/activity_log.html',{'log':plog,'nbar':'problemeditor'})

@login_required
def redirectproblem(request,pk):
    p = get_object_or_404(Problem,pk=pk)
    if p.type_new not in request.user.userprofile.user_type_new.allowed_types.all():
        raise Http404("Unauthorized")
    if p.type_new.is_contest == True:
        return redirect('/problemeditor/contest/bytest/'+p.type_new.type+'/'+p.test_label+'/'+p.label+'/')
    else:
        if p.type_new.is_sourced == True:
            if p.source.source_type.name == 'book':
                return redirect('/problemeditor/sources/book/'+str(p.source.pk)+'/'+str(p.book_chapter.pk)+'/'+str(p.pk)+'/')
            if p.source.source_type.name == 'contest':
                return redirect('/problemeditor/sources/contest/'+str(p.source.pk)+'/'+str(p.pk)+'/')
            if p.source.source_type.name == 'person':
                return redirect('/problemeditor/sources/person/'+str(p.source.pk)+'/'+str(p.pk)+'/')
        else:
            return redirect('/problemeditor/CM/bytopic/'+p.type_new.type+'/'+str(p.pk)+'/')
    

#######THIS MUST BE UPDATED TO USE ROUNDS PROPERLY.
@login_required
def uploadcontestview(request,type):
    typ = get_object_or_404(Type, type = type)
    if typ.default_question_type == 'mc' or typ.default_question_type == 'mcsa':
        return render(request,'randomtest/error_page.html',{'error_message':"Multiple choice questions currently not supported.",'nbar':'problemeditor'})
    if request.POST and request.FILES:
        form = UploadContestForm(request.POST, request.FILES,type = type)
        if form.is_valid():
            contestfile = form.cleaned_data["contestfile"]
            year = form.cleaned_data['year']
            formletter=''
            if 'formletter' in form.cleaned_data:
                formletter = form.cleaned_data['formletter']
            if 'round' in form.cleaned_data:
                round = get_object_or_404(Round, pk=form.cleaned_data['round'])
                readablelabel = year + ' ' + round.readable_label_pre_form + formletter
                default_question_type = round.default_question_type
                readablelabel = readablelabel.rstrip()
                post_label = round.readable_label_post_form
                label = year + round.name.replace(' ','') + formletter#####no spaces
            else:
                readablelabel = year + ' ' + typ.readable_label_pre_form + formletter
                default_question_type = typ.default_question_type
                readablelabel = readablelabel.rstrip()
                post_label = typ.readable_label_post_form
                label = year + type + formletter#####
            if contestfile.multiple_chunks()== True:
                pass
            else:
                f=contestfile.read().decode('utf-8')
#                print(f.decode("utf-8"))
                problemtexts = str(f).split('=========')
#Currently no support for 'mc'
                if default_question_type == 'sa':
                    sa = QuestionType.objects.get(question_type = 'short answer')

                    num = 1
                    prefix_pn = ''
                    for i in range(1,len(problemtexts)):
                        ptext = problemtexts[i]
                        if '===' in ptext:
                            prefix_pn = ptext[ptext.index('===') + 3]
                            num = 1
                        else:
                            p = Problem(problem_text = ptext,
                                        answer = '',
                                        sa_answer = '',
                                        label = label + prefix_pn + str(num),
                                        readable_label = readablelabel + post_label + prefix_pn + str(num),
                                        type_new = typ,
                                        question_type_new = sa,
                                        problem_number = num,
                                        year = year,
                                        form_letter = formletter,
                                        test_label = label,
                                        top_solution_number = 0,
                                        problem_number_prefix = prefix_pn
                                        )
                            p.save()
                            if 'round' in form.cleaned_data:
                                p.round = round
                            p.types.add(typ)
                            p.question_type.add(sa)
                            p.save()
                            compileasy(p.mc_problem_text,p.label)
                            compileasy(p.problem_text,p.label)
                            compiletikz(p.mc_problem_text,p.label)
                            compiletikz(p.problem_text,p.label)
                            p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                            p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                            p.save()
                            num+=1
                if default_question_type=='pf':
                    pf = QuestionType.objects.get(question_type = 'proof')
                    num = 1
                    prefix_pn = ''
                    for i in range(1,len(problemtexts)):
                        ptext=problemtexts[i]
                        if '===' in ptext:
                            prefix_pn = ptext[ptext.index('===') + 3]
                            num = 1
                        else:
                            p=Problem(problem_text = ptext,
                                      label = label + prefix_pn + str(num),
                                      readable_label = readablelabel + post_label + prefix_pn + str(num),
                                      type_new = typ,
                                      question_type_new = pf,
                                      problem_number = num,
                                      year = year,
                                      form_letter = formletter,
                                      test_label = label,
                                      top_solution_number = 0,
                                      problem_number_prefix = prefix_pn,
                                      )
                            p.save()
                            if 'round' in form.cleaned_data:
                                p.round = round
                            p.types.add(typ)
                            p.question_type.add(pf)
                            p.save()
                            compileasy(p.mc_problem_text,p.label)
                            compileasy(p.problem_text,p.label)
                            compiletikz(p.mc_problem_text,p.label)
                            compiletikz(p.problem_text,p.label)
                            p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                            p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                            p.save()
                            num += 1
                P = Problem.objects.filter(test_label = label)

                if len(P) > 0:
                    t = Test(name = readablelabel)
                    t.save()
                for i in P:
                    t.problems.add(i)
                    t.types.add(typ)
                t.save()
                tc,boolcreated=TestCollection.objects.get_or_create(name=typ.label)
                tc.tests.add(t)
                tc.save()
                return redirect('/problemeditor/')
    form = UploadContestForm(type = type)
    return render(request, 'problemeditor/addcontestfileform.html', context = {'form':form,'nbar':'problemeditor','typ':typ})


@login_required
def uploadpreview(request,type):
    typ = get_object_or_404(Type, type = type)
    if typ.default_question_type == 'mc' or typ.default_question_type == 'mcsa':
        return render(request,'randomtest/error_page.html',{'error_message':"Multiple choice questions currently not supported.",'nbar':'problemeditor'})
    if request.POST and request.FILES:
        form = UploadContestForm(request.POST, request.FILES,type = type)
        if form.is_valid():
            contestfile = form.cleaned_data["contestfile"]
            year = form.cleaned_data['year']
            formletter=''
            if 'formletter' in form.cleaned_data:
                formletter = form.cleaned_data['formletter']
            if 'round' in form.cleaned_data:
                round = get_object_or_404(Round, pk=form.cleaned_data['round'])
                readablelabel = year + ' ' + round.readable_label_pre_form + formletter
                default_question_type = round.default_question_type
                readablelabel = readablelabel.rstrip()
                post_label = round.readable_label_post_form
                label = year + round.name.replace(' ','') + formletter#####no spaces
            else:
                readablelabel = year + ' ' + typ.readable_label_pre_form + formletter
                default_question_type = typ.default_question_type
                readablelabel = readablelabel.rstrip()
                post_label = typ.readable_label_post_form
                label = year + type + formletter#####
            if contestfile.multiple_chunks()== True:
                pass
            else:
                f=contestfile.read().decode('utf-8')
                problemtexts = str(f).split('=========')
#Currently no support for 'mc'
                if default_question_type == 'sa' or default_question_type == 'pf':
                    rows = []
                    num = 1
                    prefix_pn = ''
                    for i in range(1,len(problemtexts)):
                        ptext = problemtexts[i]
                        if '===' in ptext:
                            prefix_pn = ptext[ptext.index('===') + 3]
                            num = 1
                        else:
                            rows.append((
                                    newtexcode(ptext,label + prefix_pn + str(num),'',temp = True),
                                    readablelabel + post_label + prefix_pn + str(num)
                                    ))
                            plabel = label + prefix_pn + str(num)
                            compileasy(ptext,plabel,temp = True)
                            compiletikz(ptext,plabel,temp = True)
#can I make the above stuff temp?
                            num+=1
                return render(request,'problemeditor/uploadpreview.html',context={'nbar': 'problemeditor','rows':rows, 'name':readablelabel})
    return redirect('/problemeditor/')


@login_required
def htmltolatex(request,type2):
    typ = get_object_or_404(Type, type = type2)
    if request.method == "POST":
        form = HTMLLatexForm(request.POST)
        if form.is_valid():
            soup = BeautifulSoup(form.cleaned_data['html_code'],'html')
            X= soup.find_all('div', class_="cmty-view-post-item-text")
            M=[]
            for i in X:
                L=i.contents
                s=''
                for j in L:
                    if type(j)==bs4.element.NavigableString:
#                        s+=str(unicode(j).replace(u'\u2019','\'').replace(u'\u201c','\"').replace(u'\u201d','\"'))
                        s += str(j)
                    elif type(j)==bs4.element.Tag:
                        if j.name=='img':
                            s+=str(j.attrs['alt'])
                        if j.name=='span' and "style" in j.attrs:
                            R=j.contents
                            for k in R:
                                if k.name=='img':
                                    s+=str(k.attrs['alt'])
                                else:
#                                    s+=str(unicode(k).replace(u'\u2019','\'').replace(u'\u201c','\"').replace(u'\u201d','\"'))
                                    s += str(k)
#                    if j.name=='span' and "style" not in j.attrs:
#                        print j
                        if j.name=='i':
                            s+=str(j).replace("<i>","$\\textit{").replace("</i>","}$")
                        if j.name=='b':
                            s+=str(j).replace("<b>","$\\textbf{").replace("</b>","}$")
#                else:
#                    print type(j)
                s=s.replace('[asy]','\n\\begin{center}\n\\begin{asy}\n')
                s=s.replace('[/asy]','\\end{asy}\n\\end{center}\n')
                M.append(s)
            return_string = ''
            for i in M:
                return_string += '=========\n\n'+str(i)+'\n\n'
            filename = "latex_code.txt"
            response = HttpResponse(return_string, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
            return response
    form = HTMLLatexForm()
    return render(request,'problemeditor/htmltolatex.html',context = {'nbar':'problemeditor','form':form,'typ':typ})

@login_required
def duplicate_view(request,type_name):
    typ=get_object_or_404(Type,type=type_name)
    problems=typ.problem_set.annotate(c=Count('duplicate_problems')).filter(c__gt=0).order_by('year')
    return render(request,'problemeditor/duplicate_view.html',context={'typ':typ,'problems':problems})


#@user_passes_test(lambda u: u.is_superuser)
@login_required
def tageditview(request):
    root_tag=NewTag.objects.get(tag='root')
    context={'nbar': 'problemeditor','root_tag':root_tag}
    return render(request,'problemeditor/tageditview.html',context)


class TagUpdateView(UpdateView):
    model = NewTag
    form_class = NewTagForm##
    template_name = 'problemeditor/tag_edit_form.html'##

    def dispatch(self, *args, **kwargs):
        self.tag_id = kwargs['pk']
        return super(TagUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        form.instance.tag=str(form.instance)
        form.instance.save()
        if form.instance.level<3:
            for child in form.instance.children.all():
                child.tag=str(child)
                child.save()
                if child.level<3:
                    for cchild in child.children.all():
                        cchild.tag=str(cchild)
                        cchild.save()
        tag = NewTag.objects.get(id=self.tag_id)
        return redirect('/problemeditor/tags/')

    def get_object(self, queryset=None):
        return get_object_or_404(NewTag, pk=self.tag_id)

class TagCreateView(CreateView):
    model = NewTag
    form_class = AddNewTagForm
    template_name = 'problemeditor/tag_add_form.html'

    def dispatch(self, *args, **kwargs):
        self.parent_tag_id = kwargs['pk']
        return super(TagCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        parent_tag = NewTag.objects.get(id=self.parent_tag_id)
        if parent_tag.children.filter(label=form.instance.label).exists():
#            form.add_error('label',forms.ValidationError(('Tag already exists'), code='invalid'))

            messages.error(self.request,'Tag already exists')
            return redirect('/problemeditor/tags')

#            return super(TagCreateView,self).form_invalid(form)
        form.save()
        form.instance.parent = parent_tag
        form.instance.level = parent_tag.level + 1
        form.save()
        form.instance.tag = str(form.instance)
        form.instance.save()
        return redirect('/problemeditor/tags/')

#    def get_object(self, queryset=None):
#        return get_object_or_404(NewTag, pk=self.tag_id)
    def get_context_data(self, *args, **kwargs):
        context = super(TagCreateView,self).get_context_data(*args,**kwargs)
        context['parent_tag'] = NewTag.objects.get(id=self.parent_tag_id)
        return context

    def get_initial(self):
        return {'parent': NewTag.objects.get(id=self.parent_tag_id)}
#    def get_form_kwargs(self, **kwargs):
#        form_kwargs = super(TagCreateView, self).get_form_kwargs(**kwargs)
#        form_kwargs['parent'] = NewTag.objects.get(id=self.parent_tag_id)
#        print(form_kwargs)
#        return form_kwargs




class TagDeleteView(DeleteView):
    model = NewTag
    template_name = 'problemeditor/tag_delete_form.html'
    success_url = "/problemeditor/tags/"

    def dispatch(self, *args, **kwargs):
        self.tag_id = kwargs['pk']
        return super(TagDeleteView, self).dispatch(*args, **kwargs)


    def get_object(self, queryset=None):
        return get_object_or_404(NewTag, pk=self.tag_id)
    def get_context_data(self, *args, **kwargs):
        context = super(TagDeleteView,self).get_context_data(*args,**kwargs)
        context['tag'] = NewTag.objects.get(id=self.tag_id)
        return context

@login_required
def taginfoview(request,pk):
    types=request.user.userprofile.user_type_new.allowed_types.all()
    tag=get_object_or_404(NewTag,pk=pk)
    rows=[]
    for typ in types:
        rows.append((typ.label,tag.problems.filter(type_new=typ).count()))
    return render(request,'problemeditor/tag_info_view.html',{'rows':rows,'tag':tag})

class TagProblemList(ListView):
    model = Problem
    template_name = 'problemeditor/tag_problem_list.html'
    paginate_by = 10
    def get_queryset(self):
        self.tag = get_object_or_404(NewTag,pk=self.args[0])
        return self.tag.problems.filter(type_new__in=self.request.user.userprofile.user_type_new.allowed_types.all()).order_by('type_new')
    def get_context_data(self, **kwargs):
        context = super(TagProblemList, self).get_context_data(**kwargs)

        userprofile = self.request.user.userprofile#
        owned_groups = userprofile.problem_groups.all()#
        editable_groups = userprofile.editable_problem_groups.all()#
        probgroups = list(chain(owned_groups,editable_groups))#

        context['tag'] = self.tag
        context['tags'] = NewTag.objects.exclude(label = 'root')
        context['nbar'] = 'problemeditor'
        context['probgroups'] = probgroups
        return context

@login_required
def remove_duplicate_problem(request,**kwargs):
    pk = request.GET.get('pk','')
    dpk = request.GET.get('dpk','')
    prob=get_object_or_404(Problem,pk=pk)
    div_code = ""
    if request.user.userprofile.user_type_new.name == 'super' or request.user.userprofile.user_type_new.name == 'contestmod':
        if prob.duplicate_problems.filter(pk=dpk).exists():
            prob.duplicate_problems.remove(Problem.objects.get(pk=dpk))
            prob.save()
    return JsonResponse({'duplicate_problems':render_to_string('problemeditor/problem-snippets/components/duplicateproblemlist.html',{'prob':prob,'request':request})})

@login_required
def add_duplicate_problem(request, **kwargs):
    pk = request.GET.get('original-prob_pk','')
    prob = get_object_or_404(Problem,pk=pk)
    linked_problem_label = request.GET.get("linked_problem_label","")
    if Problem.objects.filter(label=linked_problem_label).exists():
        q=Problem.objects.get(label=linked_problem_label)
        prob.duplicate_problems.add(q)
        prob.save()
        return JsonResponse({'duplicate_problems':render_to_string('problemeditor/problem-snippets/components/duplicateproblemlist.html',{'prob':prob,'request':request}),'status':1,'prob_pk':pk})
    return JsonResponse({'status':0,'prob_pk':pk})

@login_required
def load_edit_answer(request,**kwargs):
    pk = request.GET.get('pk','')
    qt = request.GET.get('qt','')
    prob = get_object_or_404(Problem,pk=pk)
    if qt == 'mc':
        form = EditMCAnswer(instance = prob)
    else:
        form = EditSAAnswer(instance = prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/modals/modal-edit-answer.html',{'form': form,'qt':qt})})

@login_required
def save_answer(request,**kwargs):
    pk = request.POST.get('ea_prob_pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    qt = request.POST.get('ea_qt','')
    if qt == 'mc':
        form = EditMCAnswer(request.POST,instance = prob)
        form.save()
        return JsonResponse({'qt':qt,'pk':pk,'answer':form.instance.mc_answer})
    elif qt == 'sa':
        form = EditSAAnswer(request.POST,instance = prob)
        form.save()
        return JsonResponse({'qt':qt,'pk':pk,'answer':form.instance.sa_answer})

@login_required
def load_edit_latex(request,**kwargs):
    pk = request.GET.get('pk','')
    qt = request.GET.get('qt','')
    prob = get_object_or_404(Problem,pk=pk)
    if qt == 'mc':
        form = MCProblemTextForm(instance = prob)
    else:
        form = SAProblemTextForm(instance = prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/modals/modal-edit-latex.html',{'form': form,'qt':qt})})


@login_required
def save_latex(request,**kwargs):
    pk = request.POST.get('pt_prob_pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    qt = request.POST.get('pt_qt','')
    if qt == 'mc':
        form = MCProblemTextForm(request.POST,instance = prob)
        form.save()
        prob = form.instance
        prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,prob.answers())
        prob.save()
        compileasy(prob.mc_problem_text,prob.label)
        compiletikz(prob.mc_problem_text,prob.label)
        LogEntry.objects.log_action(
            user_id = request.user.id,
            content_type_id = ContentType.objects.get_for_model(prob).pk,
            object_id = prob.id,
            object_repr = prob.label,
            action_flag = CHANGE,
            change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
            )
        return JsonResponse({'qt':qt,'pk':pk,'prob-text':render_to_string('problemeditor/problem-snippets/components/autoescapelinebreaks.html',{'string_text':form.instance.display_mc_problem_text})})
    elif qt == 'sa':
        form = SAProblemTextForm(request.POST,instance = prob)
        form.save()
        prob = form.instance
        prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
        prob.save()
        compileasy(prob.problem_text,prob.label)
        compiletikz(prob.problem_text,prob.label)
        LogEntry.objects.log_action(
            user_id = request.user.id,
            content_type_id = ContentType.objects.get_for_model(prob).pk,
            object_id = prob.id,
            object_repr = prob.label,
            action_flag = CHANGE,
            change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
            )
        return JsonResponse({'qt':qt,'pk':pk,'prob-text':render_to_string('problemeditor/problem-snippets/components/autoescapelinebreaks.html',{'string_text':form.instance.display_problem_text})})

@login_required
def view_mc_latex(request,**kwargs):
    pk = request.GET.get('pk','')
    prob = get_object_or_404(Problem,pk=pk)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/modals/modal-view-latex.html',{'prob':prob})})


class SolutionView(DetailView):
    model = Problem
    template_name = 'problemeditor/problem-snippets/modals/load_sol.html'

    def dispatch(self, *args, **kwargs):
        self.item_id = kwargs['pk']
        return super(SolutionView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Problem, pk=self.item_id)

@login_required
def load_new_solution(request,**kwargs):
    pk = request.GET.get('pk','')
    prob = get_object_or_404(Problem,pk=pk)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/modals/modal-new-solution.html',{'prob':prob})})

@login_required
def save_new_solution(request,**kwargs):
    pk = request.POST.get('ns-pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol_text = request.POST.get("new_solution_text","")
    sol_num = prob.top_solution_number+1
    prob.top_solution_number = sol_num
    prob.save()
    sol = Solution(solution_text = sol_text,solution_number = sol_num,problem_label = prob.label,parent_problem = prob)
    sol.save()
    sol.authors.add(request.user)
    sol.save()
    compileasy(sol.solution_text,prob.label,sol='sol'+str(sol_num))
    compiletikz(sol.solution_text,prob.label,sol='sol'+str(sol_num))
    sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
    sol.save()
    prob.solutions.add(sol)
    prob.save()
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(sol).pk,
        object_id = sol.id,
        object_repr = prob.label+' sol '+str(sol.solution_number),
        action_flag = ADDITION,
        change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
        )
    return JsonResponse({'pk':pk,'sol_count':prob.solutions.count()})

def delete_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol =  get_object_or_404(Solution,pk=spk)
    if request.user.userprofile.user_type_new.name == 'super' or request.user.userprofile.user_type_new.name == 'sitemanager' or request.user.userprofile.user_type_new.name == 'contestmanager' or request.user.userprofile.user_type_new.name == 'contestmod':
        if prob.type_new in request.user.userprofile.user_type_new.allowed_types.all():
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = prob.label+' sol '+str(sol.solution_number),
                action_flag = DELETION,
                change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
                )
            sol.delete()
            return JsonResponse({'deleted':1,'sol_count': prob.solutions.count()})
    return JsonResponse({'deleted':0})

@login_required
def add_tag(request):
    tags = [(d,p) for d, p in request.POST.items() if d.startswith('addtag')]
    for i in tags:
        problem_pk=i[0].split('_')[1]
        prob=get_object_or_404(Problem,pk=problem_pk)
        tag = get_object_or_404(NewTag,pk=i[1])
        if tag.problems.filter(pk=problem_pk).exists():
            return JsonResponse({'prob_pk':problem_pk,'status':1,'tag_count':prob.newtags.count()})
        prob.newtags.add(tag)
        prob.save()
    return JsonResponse({'prob_pk':problem_pk,'status':0,'tag_list':render_to_string("problemeditor/problem-snippets/components/tag_snippet.html",{'prob':prob})})


@login_required
def delete_tag(request):
    delete_tag=request.POST.get('problem_tag_id','')
    del_list=delete_tag.split('_')
    problem_pk=del_list[1]
    prob=get_object_or_404(Problem,pk=problem_pk)
    tag_pk = del_list[2]
    tag = get_object_or_404(NewTag,pk=tag_pk)
    prob.newtags.remove(tag)
    prob.save()
    L= prob.newtags.all()
    response_string = render_to_string("problemeditor/problem-snippets/components/tag_snippet.html",{'prob':prob})
    return JsonResponse({'prob_pk':problem_pk,'tag_list':response_string,'tag_count':prob.newtags.count()})


@login_required
def change_needs_answers(request,**kwargs):
    pk = request.POST.get('pk','')
    na = request.POST.get('na','')
    prob = get_object_or_404(Problem,pk=pk)
    prob.needs_answers = int(na)
    prob.save()
    return JsonResponse({'s':1})

@login_required
def load_edit_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol =  get_object_or_404(Solution,pk=spk)
    form = SolutionForm(instance=sol)
    return JsonResponse({'sol_form':render_to_string('problemeditor/problem-snippets/modals/edit_sol_form.html',{'form':form,'prob':prob})})

@login_required
def save_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol =  get_object_or_404(Solution,pk=spk)

    sol.solution_text = request.POST.get('solution_text')
    sol.modified_date = timezone.now()
    sol.authors.add(request.user)
    sol.save()
    compileasy(sol.solution_text,prob.label,sol='sol'+str(sol.solution_number))
    compiletikz(sol.solution_text,prob.label,sol='sol'+str(sol.solution_number))
    sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
    sol.save()
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(sol).pk,
        object_id = sol.id,
        object_repr = prob.label+' sol '+str(sol.solution_number),
        action_flag = CHANGE,
        change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
        )
    return JsonResponse({'sol_text':render_to_string('problemeditor/problem-snippets/modals/soltext.html',{'solution':sol})})

@login_required
def change_qt(request,**kwargs):
    pk = request.POST.get('pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    form = ChangeQuestionTypeForm1(instance=prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-change-qt.html',{'form':form})})

@login_required
def change_qt_load(request,**kwargs):
    pk = request.POST.get('pk','')
    qt_pk = request.POST.get('qt_pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    qt = get_object_or_404(QuestionType,pk=qt_pk)
    if qt.question_type == "multiple choice":
        form = ChangeQuestionTypeForm2MC(instance=prob)
    elif qt.question_type == "multiple choice short answer":
        form = ChangeQuestionTypeForm2MCSA(instance=prob)
    elif qt.question_type == "short answer":
        form = ChangeQuestionTypeForm2SA(instance=prob)
    elif qt.question_type == "proof":
        form = ChangeQuestionTypeForm2PF(instance=prob)
    return JsonResponse({'cqt-form':render_to_string('problemeditor/problem-snippets/CMmodals/cqt-fields.html',{'form':form})})

@login_required
def save_qt(request,**kwargs):
    qt = get_object_or_404(QuestionType,pk=request.POST.get('question_type_new',''))
    prob = get_object_or_404(Problem,pk=request.POST.get('cqt_prob_pk',''))
    prob.question_type_new = qt
    if qt.question_type == 'proof':
        prob.problem_text = request.POST.get('problem_text')
        prob.save()
        prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
        prob.save()
        compileasy(prob.problem_text,prob.label)
        compiletikz(prob.problem_text,prob.label)
    elif qt.question_type == 'short answer':
        prob.problem_text = request.POST.get('problem_text')
        prob.sa_answer = request.POST.get('sa_answer')
        prob.save()
        prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
        prob.save()
        compileasy(prob.problem_text,prob.label)
        compiletikz(prob.problem_text,prob.label)
    elif qt.question_type == 'multiple choice':
        prob.problem_text = request.POST.get('mc_problem_text')
        prob.mc_answer = request.POST.get('mc_answer')
        prob.answer_A = request.POST.get('answer_A')
        prob.answer_B = request.POST.get('answer_B')
        prob.answer_C = request.POST.get('answer_C')
        prob.answer_D = request.POST.get('answer_D')
        prob.answer_E = request.POST.get('answer_E')
        prob.save()
        prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,prob.answers())
        prob.save()
        compileasy(prob.mc_problem_text,prob.label)
        compiletikz(prob.mc_problem_text,prob.label)
    elif qt.question_type == 'multiple choice short answer':
        prob.problem_text = request.POST.get('mc_problem_text')
        prob.mc_answer = request.POST.get('mc_answer')
        prob.answer_A = request.POST.get('answer_A')
        prob.answer_B = request.POST.get('answer_B')
        prob.answer_C = request.POST.get('answer_C')
        prob.answer_D = request.POST.get('answer_D')
        prob.answer_E = request.POST.get('answer_E')
        prob.save()
        prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,prob.answers())
        prob.save()
        compileasy(prob.mc_problem_text,prob.label)
        compiletikz(prob.mc_problem_text,prob.label)
        prob.problem_text = request.POST.get('problem_text')
        prob.sa_answer = request.POST.get('sa_answer')
        prob.save()
        prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
        prob.save()
        compileasy(prob.problem_text,prob.label)
        compiletikz(prob.problem_text,prob.label)
    return JsonResponse({'problem-div':render_to_string('problemeditor/problem-snippets/CMcomponents/problemtext.html',{'prob':prob}),'qt':qt.question_type})

@login_required
def load_change_difficulty(request,**kwargs):
    prob = get_object_or_404(Problem,pk=request.POST.get('pk',''))
    form = DifficultyForm(instance = prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-change-difficulty.html',{'form':form})})

@login_required
def save_difficulty(request,**kwargs):
    prob = get_object_or_404(Problem,pk=request.POST.get('diff_prob_pk',''))
    prob.difficulty = request.POST.get('difficulty','')
    prob.save()
    return JsonResponse({'difficulty':prob.difficulty})

@login_required
def load_edit_review(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    review = get_object_or_404(ProblemApproval,pk = request.POST.get('review_pk',''))
    form = ApprovalForm(instance = review)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-review.html',{'form':form,'edit_review':1,'prob':prob})})

@login_required
def new_review(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    form = ApprovalForm()
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-review.html',{'form':form,'prob':prob})})

@login_required
def save_review(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    review = get_object_or_404(ProblemApproval,pk = request.POST.get('rv_pk',''))
    review.author_name = request.POST.get('author_name','')
    review.approval_status = request.POST.get('approval_status','')
    review.save()
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(review).pk,
        object_id = review.id,
        object_repr = prob.label,
        action_flag = CHANGE,
        change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
        )
    return JsonResponse({'approvals':render_to_string('problemeditor/problem-snippets/CMcomponents/approval-div.html',{'prob':prob})})

@login_required
def save_new_review(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    review = ProblemApproval(author_name = request.POST.get('author_name',''),approval_status = request.POST.get('approval_status',''),approval_user=request.user)
    review.save()
    prob.approvals.add(review)
    prob.save()
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(review).pk,
        object_id = review.id,
        object_repr = prob.label,
        action_flag = ADDITION,
        change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
        )
    return JsonResponse({'approvals':render_to_string('problemeditor/problem-snippets/CMcomponents/approval-div.html',{'prob':prob})})

@login_required
def new_comment(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    form = CommentForm()
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-new-comment.html',{'form':form,'prob':prob})})

@login_required
def save_comment(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('nc-pk',''))
    com_form = CommentForm(request.POST)
    com_num=prob.comments.count()+1
    if com_form.is_valid():
        com = com_form.save(commit=False)
        com.comment_number=com_num
        com.author = request.user
        com.problem_label=prob.label
        com.save()
        prob.comments.add(com)
        prob.save()
        if prob.comments.count() > 1:
            return JsonResponse({'new_comment':0,'comment':render_to_string('problemeditor/problem-snippets/CMcomponents/comment.html',{'com':com_form.instance,'request':request,'prob':prob})})
        else:
            return JsonResponse({'new_comment':1,'comments-div':render_to_string('problemeditor/problem-snippets/CMcomponents/comments-div.html',{'prob':prob,'request':request})})
    return JsonResponse({})

def delete_comment(request, **kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    comment = get_object_or_404(Comment,pk = request.POST.get('com_pk',''))
    comment.delete()
    return JsonResponse({'comments-div':render_to_string('problemeditor/problem-snippets/CMcomponents/comments-div.html',{'prob':prob,'request':request})})



def matrixview(request,type):    
    typ = get_object_or_404(Type, type = type)
    probsoftype = Problem.objects.filter(type_new = typ)
#get function to only look at round...


#    num_untagged = probsoftype.filter(newtags__isnull = True).count()
    testlabels = []
    pot = list(probsoftype)
    for i in range(0,len(pot)):
        testlabels.append(pot[i].test_label)
    testlabels = list(set(testlabels))
    testlabels.sort()
    rows2 = []
    maxcount = 0
    if typ.type == "Putnam":
        for i in range(0,len(testlabels)):
            P = probsoftype.filter(test_label = testlabels[i]).order_by('label')
            rows2.append((testlabels[i],P))
            n = P.count()
            if n > maxcount:
                maxcount = n
    else:
        for i in range(0,len(testlabels)):
            P = probsoftype.filter(test_label = testlabels[i]).order_by('problem_number')
            rows2.append((testlabels[i],P))
            n = P.count()
            if n > maxcount:
                maxcount = n
    if typ.type =="Putnam":
        numbers = ['A1','A2','A3','A4','A5','A6','B1','B2','B3','B4','B5','B6']
    else:
        numbers = [str(i) for i in range(1,maxcount+1)]
    template = loader.get_template('problemeditor/matrixview.html')
    context = { 'type' : typ.type, 'typelabel':typ.label, 'nbar': 'problemeditor','rows2':rows2,'prefix':'bytest','numbers' : numbers}
    return HttpResponse(template.render(context,request))

def mod_permission(user):
    if user.userprofile.user_type_new.name == "super" or user.userprofile.user_type_new.name == "contestmod":
        return True
    return False

@user_passes_test(lambda u: mod_permission(u))
def edittypes(request):
    userprofile = request.user.userprofile
    return render(request,'problemeditor/edittypesview.html',{'nbar':'problemeditor','types' : userprofile.user_type_new.allowed_types.all()})

@user_passes_test(lambda u: mod_permission(u))
def load_new_type(request,**kwargs):
    form = NewTypeForm()
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-type.html',{'form':form})})

@user_passes_test(lambda u: mod_permission(u))
def save_type(request):
    if request.method == "POST":
        form = NewTypeForm(request.POST)
        if form.is_valid():
            new_type = form.save()
            super = UserType.objects.get(name="super")
            super.allowed_types.add(new_type)
            super.save()
            for i in request.POST.getlist('user_groups'):
                user_type = UserType.objects.get(pk=i)
                user_type.allowed_types.add(new_type)
                user_type.save()
        return JsonResponse({'success' : 1, 'row': render_to_string('problemeditor/edittypes-row.html',{'type':new_type})})
    return JsonResponse({'success':0})

@user_passes_test(lambda u: mod_permission(u))
def load_new_round(request,**kwargs):
    typ = get_object_or_404(Type,pk=request.GET.get('type_id'))
    form = NewRoundForm()
    form.fields['type'].initial = typ.pk
    form.fields['type'].label = typ.label
    return JsonResponse({'modal-html':render_to_string('problemeditor/modal-new-round.html',{'form':form})})

@user_passes_test(lambda u: mod_permission(u))
def save_round(request):
    if request.method == "POST":
        form = NewRoundForm(request.POST)
        if form.is_valid():
            new_round = form.save()
        return JsonResponse({'success' : 1, 'row': render_to_string('problemeditor/edittypes-round-row.html',{'round':new_round}),'type_id' : new_round.type.pk})
    return JsonResponse({'success':0})
