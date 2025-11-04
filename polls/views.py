from django.db.models import F
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from polls.forms import ChoiceForm, QuestionForm
from polls.models import Question, Choice, VoteRecord
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('polls:register')
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'User registered successfully!')
        return redirect('polls:login')
    return render(request, 'polls/register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('polls:index')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('polls:login')
    return render(request, 'polls/login.html')

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_superuser and  user != request.user:
        messages.error(request, 'You dont have permission to delete user')
        return redirect('show_context')
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('show_context')

@login_required
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_superuser and user != request.user:
        messages.error(request, 'You dont have permission to update this user')
        return redirect('polls:show_context')

    if request.method == 'POST':
        new_password = request.POST['password']
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password updated successfully!')
        return redirect('polls:show_context')

    return render(request, 'polls/update.html', {'user': user})


def show_context(request):
    if request.user.is_superuser:
        users = User.objects.all()
    else:
        users = User.objects.filter(id=request.user.id)
    registered_users = {
        user.id: {
            'username': user.username,
            'email': user.email if user.email else 'N/A' ,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M')
        }
        for user in users
    }
    context = {'registered_users': registered_users,'is_admin': request.user.is_superuser}
    return render(request, 'polls/context.html', context)


def logout_user(request):
    logout(request)
    return redirect('polls:login')

@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_superuser and  user != request.user:
        messages.error(request, 'You dont have permission to delete user')
        return redirect('show_context')
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('show_context')

@login_required
def add_question(request):
    # Only superusers can access
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to add questions.")

    ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=2, can_delete=False)

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


@login_required
def index_view(request):
    all_questions = Question.objects.order_by("-pub_date")
    voted_question_ids = VoteRecord.objects.filter(user=request.user).values_list("question_id", flat=True)
    voted_questions = all_questions.filter(id__in=voted_question_ids)
    new_questions = all_questions.exclude(id__in=voted_question_ids)
    context = {
        "voted_questions": voted_questions,
        "new_questions": new_questions,
    }
    return render(request, "polls/index.html", context)


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if VoteRecord.objects.filter(user=request.user, question=question).exists():
        voted_users = VoteRecord.objects.filter(question=question).select_related("user")
        return render(
            request,
            "polls/show_user.html",
            {
                "question": question,
                "voted_users": voted_users,
                "error_message": "You have already voted on this poll.",
            },
        )
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {"question": question, "error_message": "You didn't select a choice."},
        )
    selected_choice.votes = F("votes") + 1
    selected_choice.save()
    VoteRecord.objects.create(user=request.user, question=question,choice=selected_choice)
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

@login_required
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    has_voted = VoteRecord.objects.filter(user=request.user, question=question).exists()
    return render(request, "polls/detail.html", {"question": question, "has_voted": has_voted})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})

def delete_selected_polls(request):
    if request.method == 'POST':
        selected_id = request.POST.getlist('selected_polls')        #getlist is return list of value
        Question.objects.filter(pk__in=selected_id).delete()
    return redirect('polls:index')
@login_required
def show_voters(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    voted_users = VoteRecord.objects.filter(question=question).select_related("user", "choice")
    context = {
        "question": question,
        "voted_users": voted_users
    }
    return render(request, "polls/show_user.html", context)