from django.shortcuts import render,render_to_response, get_object_or_404,redirect
#from django.template import loader,RequestContext,Context

from django.template.loader import get_template

#from django.contrib.auth import authenticate,login,logout
#from django.contrib.auth.admin import User
from django.contrib.auth.decorators import login_required
#from django.conf import settings
#from django.contrib.admin.models import LogEntry
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import UpdateView,DetailView,ListView,CreateView
#from subprocess import Popen,PIPE
#import tempfile
#import os

from .forms import SectionForm,SubsectionForm,TextBlockForm,TheoremForm,ProofForm,HandoutForm,ImageForm
from .models import Handout,Section,DocumentElement,SubSection,TextBlock,Theorem,Proof,ImageModel
from randomtest.utils import newtexcode,compileasy
from randomtest.models import get_or_create_up,SortableProblem,NewTest,Type,Tag,Problem


from random import shuffle

# Create your views here.

@login_required
def handouteditview(request,pk):
    h=get_object_or_404(Handout,pk=pk)
    if request.method == "POST":
        form=request.POST
        if "addsection" in form:
            s=Section(name=form.get("section-name",""))
            s.save()
            d=DocumentElement(content_object=s,chapter_number=h.order,section_number=h.top_section_number+1,order=h.top_order_number+1)
            d.save()
            h.top_section_number=h.top_section_number+1
            h.top_subsection_number=0
            h.top_order_number = h.top_order_number+1
            h.top_theorem_number = 0
            h.document_elements.add(d)
            h.save()
        if "addsubsection" in form:
            s=SubSection(name=form.get("subsection-name",""))
            s.save()
            d=DocumentElement(content_object=s,chapter_number=h.order,section_number=h.top_section_number,subsection_number=h.top_subsection_number+1,order=h.top_order_number+1)
            d.save()
            h.top_subsection_number=h.top_subsection_number+1
            h.top_order_number = h.top_order_number+1
            h.top_theorem_number = 0
            h.document_elements.add(d)
            h.save()
        if "addtextblock" in form:
            textbl = form.get("codetextblock","")
            tb = TextBlock(text_code = textbl, text_display="")
            tb.save()
            tb.text_display = newtexcode(textbl, 'textblock_'+str(tb.pk), "")
            tb.save()
            compileasy(tb.text_code,'textblock_'+str(tb.pk))
            d=DocumentElement(content_object=tb,chapter_number=h.order,section_number=h.top_section_number,subsection_number=h.top_subsection_number,order=h.top_order_number+1)
            d.save()
            h.top_order_number = h.top_order_number+1
            h.document_elements.add(d)
            h.save()
        if "addtheorem" in form:
            thmbl = form.get("codetheoremblock","")
            prefix = form.get("theorem-prefix","")
            thmname = form.get("theorem-name","")
            th = Theorem(theorem_code = thmbl, theorem_display="",prefix=prefix,name=thmname,theorem_number=h.top_theorem_number+1)
            th.save()
            th.theorem_display = newtexcode(thmbl, 'theoremblock_'+str(th.pk), "")
            th.save()
            d=DocumentElement(content_object=th,chapter_number=h.order,section_number=h.top_section_number,subsection_number=h.top_subsection_number,order=h.top_order_number+1)
            d.save()
            h.top_order_number = h.top_order_number + 1
            h.top_theorem_number = h.top_theorem_number + 1
            h.document_elements.add(d)
            h.save()
        if "addproof" in form:
            proofbl = form.get("codeproofblock","")
            prefix = form.get("proof-prefix","")
            pf = Proof(proof_code = proofbl, proof_display="",prefix=prefix)
            pf.save()
            pf.proof_display = newtexcode(proofbl, 'proofblock_'+str(pf.pk), "")
            pf.save()
            d=DocumentElement(content_object=pf,chapter_number=h.order,section_number=h.top_section_number,subsection_number=h.top_subsection_number,order=h.top_order_number+1)
            d.save()
            h.top_order_number = h.top_order_number+1
            h.document_elements.add(d)
            h.save()
        if "addproblemset" in form:
            radio=form.get("neworold","")
            if radio=="new-problem-set":
                t=NewTest(name=form.get("problem-set-name",""))
                t.save()
            else:
                testtocopy=NewTest.objects.get(pk=form.get("existing-problem-set",""))
                t=NewTest(name=testtocopy.name)
                t.save()
                for p in testtocopy.problems.all():
                    sp=SortableProblem(order=p.order,problem=p.problem,newtest_pk=t.pk)
                    sp.save()
                    t.problems.add(sp)
            d=DocumentElement(content_object=t,chapter_number=h.order,section_number=h.top_section_number,subsection_number=h.top_subsection_number,order=h.top_order_number+1)
            d.save()
            h.top_order_number = h.top_order_number+1
            h.document_elements.add(d)
            h.save()
#redirect to edit newtest view?
        if "addimage" in form:
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                m = ImageModel(image=form.cleaned_data['image'])
                m.save()
                d=DocumentElement(content_object=m,chapter_number=h.order,section_number=h.top_section_number,subsection_number=h.top_subsection_number,order=h.top_order_number+1)
                d.save()
                h.top_order_number = h.top_order_number+1
                h.document_elements.add(d)
                h.save()
        if 'save' in form:
            if 'docinput' in form:
                D=list(h.document_elements.all())
                D=sorted(D,key=lambda x:x.order)
                doc_element_inputs = form.getlist('docinput')#could be an issue if no doc_elements
                section_num = 0
                subsection_num = 0
                theorem_num = 1
                for d in D:
                    if 'element_'+str(d.pk) not in doc_element_inputs:
                        d.delete()
                for i in range(0,len(doc_element_inputs)):
                    d = h.document_elements.get(pk=doc_element_inputs[i].split('_')[1])
                    d.order = i+1
                    if d.content_type.model == "section":
                        section_num += 1
                        subsection_num = 0
                        theorem_num=1
                    elif d.content_type.model == "subsection":
                        subsection_num += 1
                        theorem_num=1
                    elif d.content_type.model == "theorem":
                        th=d.content_object
                        th.theorem_number = theorem_num
                        th.save()
                        h.top_theorem_number = theorem_num
                        h.save()
                        theorem_num += 1
                    d.section_number = section_num
                    d.subsection_number = subsection_num
                    d.save()        
    doc_elements = list(h.document_elements.all())
    doc_elements = sorted(doc_elements,key=lambda x:x.order)
    return render(request, 'handouts/handouteditview.html',{'doc_elements': doc_elements,'nbar': 'viewmytests','handout':h,'mynewtests':request.user.userprofile.newtests.all()})

class HandoutUpdateView(UpdateView):
    model = Handout
    form_class = HandoutForm
    template_name = 'handouts/handout_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.handout_id = kwargs['pk']
        return super(HandoutUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        handout = Handout.objects.get(id=self.handout_id)
        return redirect('/handouts/edit/'+str(self.handout_id)+'/')

    def get_object(self, queryset=None):
        return get_object_or_404(Handout, pk=self.handout_id)


class SectionUpdateView(UpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'handouts/section_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.section_id = kwargs['spk']
        self.handout_id = kwargs['pk']
        return super(SectionUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        section = Section.objects.get(id=self.section_id)
        return redirect('/handouts/edit/'+str(self.handout_id)+'/')

    def get_object(self, queryset=None):
        return get_object_or_404(Section, pk=self.section_id)
    def get_context_data(self, *args, **kwargs):
        context = super(SectionUpdateView, self).get_context_data(*args, **kwargs)
        context['handout'] = self.handout_id
        return context

class SubsectionUpdateView(UpdateView):
    model = SubSection
    form_class = SubsectionForm
    template_name = 'handouts/subsection_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.subsection_id = kwargs['spk']
        self.handout_id = kwargs['pk']
        return super(SubsectionUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        subsection = SubSection.objects.get(id=self.subsection_id)
        return redirect('/handouts/edit/'+str(self.handout_id)+'/')

    def get_object(self, queryset=None):
        return get_object_or_404(SubSection, pk=self.subsection_id)
    def get_context_data(self, *args, **kwargs):
        context = super(SubsectionUpdateView, self).get_context_data(*args, **kwargs)
        context['handout'] = self.handout_id
        return context

                      

class TextBlockUpdateView(UpdateView):
    model = TextBlock
    form_class = TextBlockForm
    template_name = 'handouts/textblock_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.textblock_id = kwargs['spk']
        self.handout_id = kwargs['pk']
        return super(TextBlockUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        textblock = TextBlock.objects.get(id=self.textblock_id)
        textblock.text_display = newtexcode(textblock.text_code, 'textblock_'+str(textblock.pk), "")
        compileasy(textblock.text_code,'textblock_'+str(textblock.pk))
        return redirect('/handouts/edit/'+str(self.handout_id)+'/')

    def get_object(self, queryset=None):
        return get_object_or_404(TextBlock, pk=self.textblock_id)
    def get_context_data(self, *args, **kwargs):
        context = super(TextBlockUpdateView, self).get_context_data(*args, **kwargs)
        context['handout'] = self.handout_id
        return context

class TheoremUpdateView(UpdateView):
    model = Theorem
    form_class = TheoremForm
    template_name = 'handouts/theorem_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.theorem_id = kwargs['spk']
        self.handout_id = kwargs['pk']
        return super(TheoremUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        theorem = Theorem.objects.get(id=self.theorem_id)
        theorem.theorem_display = newtexcode(theorem.theorem_code, 'theoremblock_'+str(theorem.pk), "")
        compileasy(theorem.theorem_code,'theoremblock_'+str(theorem.pk))
        return redirect('/handouts/edit/'+str(self.handout_id)+'/')

    def get_object(self, queryset=None):
        return get_object_or_404(Theorem, pk=self.theorem_id)
    def get_context_data(self, *args, **kwargs):
        context = super(TheoremUpdateView, self).get_context_data(*args, **kwargs)
        context['handout'] = self.handout_id
        return context

                      

class ProofUpdateView(UpdateView):
    model = Proof
    form_class = ProofForm
    template_name = 'handouts/proof_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.proof_id = kwargs['spk']
        self.handout_id = kwargs['pk']
        return super(ProofUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        proof = Proof.objects.get(id=self.proof_id)
        proof.proof_display = newtexcode(proof.proof_code, 'proofblock_'+str(proof.pk), "")
        compileasy(proof.proof_code,'proofblock_'+str(proof.pk))
        return redirect('/handouts/edit/'+str(self.handout_id)+'/')

    def get_object(self, queryset=None):
        return get_object_or_404(Proof, pk=self.proof_id)
    def get_context_data(self, *args, **kwargs):
        context = super(ProofUpdateView, self).get_context_data(*args, **kwargs)
        context['handout'] = self.handout_id
        return context

@login_required
def handoutlistview(request):
    userprofile = get_or_create_up(request.user)
    if request.method == "POST":
        form=request.POST
        if "addhandout" in form:
            h=Handout(name=form.get("handout-name",""))
            h.save()
            userprofile.handouts.add(h)
            userprofile.save()

    handouts=userprofile.handouts.all()
    return render(request, 'handouts/handoutlistview.html',{'object_list': handouts,'nbar': 'viewmytests'})


@login_required
def editnewtestview(request,pk,hpk):
    h=get_object_or_404(Handout,pk=pk)
    T=get_object_or_404(NewTest,pk=hpk)
    Tprobs=T.problems.all()
    if request.method == "POST":
        if 'save' in request.POST:
            form=request.POST
            if 'probleminput' in form:
                P=list(T.problems.all())
                P=sorted(P,key=lambda x:x.order)
                probinputs=form.getlist('probleminput')#could be an issue if no problems             
                for prob in P:
                    if 'problem_'+str(prob.pk) not in probinputs:
                        prob.delete()
                for i in range(0,len(probinputs)):
                    prob=T.problems.get(pk=probinputs[i].split('_')[1])
                    prob.order=i+1
                    prob.save()
            return redirect('../../')
        if 'addproblems' in request.POST:
            form=request.POST
            testtype = form.get('testtype','')
            searchterm = form.get('keywords','')
            if searchterm is None or searchterm==u'':
                keywords=[]
            else:
                keywords=searchterm.split(' ')

            num=form.get('numproblems','')
            if num is None or num==u'':
                num=10
            else:
                num=int(num)

            tag=form.get('tag','')
            if tag=="Unspecified":
                tag=''

            probbegin=form.get('probbegin','')
            if probbegin is None or probbegin==u'':
                probbegin=0
            else:
                probbegin=int(probbegin)

            probend=form.get('probend','')
            if probend is None or probend==u'':
                probend=10000
            else:
                probend=int(probend)

            yearbegin=form.get('yearbegin','')
            if yearbegin is None or yearbegin==u'':
                yearbegin=0
            else:
                yearbegin=int(yearbegin)
            yearend=form.get('yearend','')
            if yearend is None or yearend==u'':
                yearend=10000
            else:
                yearend=int(yearend)

            if len(tag)>0:
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype)
                P=P.filter(tags__in=Tag.objects.filter(tag__startswith=tag)).distinct()
            else:
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype).distinct()
            for i in keywords:
                P=P.filter(Q(problem_text__contains=i)|Q(mc_problem_text__contains=i)|Q(label=i)|Q(test_label=i))
            blocked_probs = Tprobs.values('problem_id')
            P=P.exclude(id__in=blocked_probs)
            P=list(P)
            P=sorted(P,key=lambda x:x.problem_number)
#            shuffle(P)
            P=P[0:min(50,num)]
            t=Tprobs.count()
            for i in range(t,t+len(P)):
                sp=SortableProblem(problem=P[i-t],order=i+1,newtest_pk=T.pk)
                sp.save()
                T.problems.add(sp)
            T.num_problems=T.problems.count()
            T.save()
    userprofile = get_or_create_up(request.user)
    if userprofile.user_type == 'member':
        types=list(Type.objects.exclude(type__startswith="CM"))
    elif userprofile.user_type == 'manager':
        types=list(Type.objects.filter(type__startswith="CM"))
    elif userprofile.user_type == 'super':
        types=list(Type.objects.all())
    tags=sorted(list(Tag.objects.all()),key=lambda x:x.tag)
    rows=[]
    for i in range(0,len(types)):
        rows.append((types[i].type,types[i].label))
    rows=sorted(rows,key=lambda x:x[1])
    P=list(Tprobs)
    P=sorted(P,key=lambda x:x.order)
    tags=sorted(list(Tag.objects.all()),key=lambda x:x.tag)
    return render(request, 'handouts/newtesteditview.html',{'sortableproblems': P,'nbar': 'viewmytests','test':T,'rows':rows,'tags':tags,'handout':h})
