from django.db.models import F
from django.forms import inlineformset_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from polls.forms import ChoiceForm, QuestionForm
from polls.models import Question, Choice

def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(request,"polls/detail.html",{
                "question": question,
                "error_message": "You didn't select a choice."})
    else:
        selected_choice.votes = F("votes") + 1        # F used for directly on field values for addition
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

def index_view(request):
    question_list = Question.objects.order_by("-pub_date")[:5]            # :5 use slicing for get latest five question
    context = {"latest_question_list": question_list}
    return render(request, "polls/index.html", context)

def add_question(request):
    ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=2, can_delete=False )
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if question_form.is_valid() and formset.is_valid():
            question = question_form.save()
            choices = formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()
            return redirect('polls:index')
    else:
        question_form = QuestionForm()
        formset = ChoiceFormSet()

    return render(request, 'polls/add_question.html', {
        'question_form': question_form,
        'formset': formset
    })

def delete_selected_polls(request):
    if request.method == 'POST':
        selected_id = request.POST.getlist('selected_polls')        #getlist is return list of value
        Question.objects.filter(pk__in=selected_id).delete()
    return redirect('polls:index')