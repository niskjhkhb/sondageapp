from django.db import transaction
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from sondages.models import Survey, Question, Answer, Response
from sondages.forms import SurveyForm, QuestionForm, OptionForm, AnswerForm, BaseAnswerFormSet


@login_required
def survey_list(request):
    """User can view all their surveys"""
    surveys = Survey.objects.filter(creator=request.user).order_by("-created_at").all()
    return render(request, "sondages/list.html", {"surveys": surveys})


@login_required
def detail(request, pk):
    """User can view an active survey"""
    try:
        survey = Survey.objects.prefetch_related("question_set__option_set").get(
            pk=pk, creator=request.user, is_active=True
        )
    except Survey.DoesNotExist:
        raise Http404()

    questions = survey.question_set.all()

    # Calculate the results.
    # This is a naive implementation and it could be optimised to hit the database less.
    # See here for more info on how you might improve this code: https://docs.djangoproject.com/en/3.1/topics/db/aggregation/
    for question in questions:
        option_pks = question.option_set.values_list("pk", flat=True)
        total_answers = Answer.objects.filter(option_id__in=option_pks).count()
        for option in question.option_set.all():
            num_answers = Answer.objects.filter(option=option).count()
            option.percent = 100.0 * num_answers / total_answers if total_answers else 0

    host = request.get_host()
    public_path = reverse("survey-start", args=[pk])
    public_url = f"{request.scheme}://{host}{public_path}"
    num_submissions = survey.responses.filter().count()
    return render(
        request,
        "sondages/detail.html",
        {
            "survey": survey,
            "public_url": public_url,
            "questions": questions,
            "num_submissions": num_submissions,
        },
    )


@login_required
def create(request):
    """User can create a new survey"""
    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.creator = request.user
            survey.save()
            return redirect("survey-edit", pk=survey.id)
    else:
        form = SurveyForm()

    return render(request, "sondages/create.html", {"form": form})


@login_required
def delete(request, pk):
    """User can delete an existing survey"""
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    if request.method == "POST":
        survey.delete()

    return redirect("survey-list")


@login_required
def edit(request, pk):
    """User can add questions to a draft survey, then acitvate the survey"""
    try:
        survey = Survey.objects.prefetch_related("question_set__option_set").get(
            pk=pk, creator=request.user, is_active=False
        )
    except Survey.DoesNotExist:
        raise Http404()

    if request.method == "POST":
        survey.is_active = True
        survey.save()
        return redirect("survey-detail", pk=pk)
    else:
        questions = survey.question_set.all()
        return render(request, "sondages/edit.html", {"survey": survey, "questions": questions})


@login_required
def question_create(request, pk):
    """User can add a question to a draft survey"""
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.save()
            return redirect("survey-option-create", survey_pk=pk, question_pk=question.pk)
    else:
        form = QuestionForm()

    return render(request, "sondages/question.html", {"survey": survey, "form": form})


@login_required
def option_create(request, survey_pk, question_pk):
    """User can add options to a survey question"""
    survey = get_object_or_404(Survey, pk=survey_pk, creator=request.user)
    question = Question.objects.get(pk=question_pk)
    if request.method == "POST":
        form = OptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.question_id = question_pk
            option.save()
    else:
        form = OptionForm()

    options = question.option_set.all()
    return render(
        request,
        "sondages/options.html",
        {"survey": survey, "question": question, "options": options, "form": form},
    )


def start(request, pk):
    """Survey-taker can start a survey"""
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    if request.method == "POST":
        response = Response.objects.create(survey=survey)
        return redirect("survey-submit", survey_pk=pk, sub_pk=response.pk)

    return render(request, "sondages/start.html", {"survey": survey})


def submit(request, survey_pk, sub_pk):
    """Survey-taker submit their completed survey."""
    try:
        survey = Survey.objects.prefetch_related("question_set__option_set").get(
            pk=survey_pk, is_active=True
        )
    except Survey.DoesNotExist:
        raise Http404()

    try:
        response = survey.responses.get(pk=sub_pk)
    except Response.DoesNotExist:
        raise Http404()

    questions = survey.question_set.all()
    options = [q.option_set.all() for q in questions]
    form_kwargs = {"empty_permitted": False, "options": options}
    AnswerFormSet = formset_factory(AnswerForm, extra=len(questions), formset=BaseAnswerFormSet)
    if request.method == "POST":
        formset = AnswerFormSet(request.POST, form_kwargs=form_kwargs)
        if formset.is_valid():
            with transaction.atomic():
                for form in formset:
                    Answer.objects.create(
                        response_id=response.pk,
                        question=form.cleaned_data.get("question"),
                        text_answer=form.cleaned_data.get("text_answer", ""),
                        scale_value=form.cleaned_data.get("scale_value"),
                    )
            return redirect("survey-thanks", pk=survey_pk)

    else:
        formset = AnswerFormSet(form_kwargs=form_kwargs)

    question_forms = zip(questions, formset)
    return render(
        request,
        "sondages/submit.html",
        {"survey": survey, "question_forms": question_forms, "formset": formset},
    )


def thanks(request, pk):
    """Survey-taker receives a thank-you message."""
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    return render(request, "sondages/thanks.html", {"survey": survey})


@login_required
def dashboard(request):
    """User can view their dashboard with survey stats"""
    total_surveys = Survey.objects.filter(creator=request.user).count()
    total_responses = Answer.objects.filter(response__survey__creator=request.user).count()
    active_surveys = Survey.objects.filter(creator=request.user, is_active=True).count()

    context = {
        "total_surveys": total_surveys,
        "total_responses": total_responses,
        "active_surveys": active_surveys,
    }
    return render(request, "sondages/dashboard.html", context)


def check_auth(request):
    """Check if user is authenticated and return status"""
    return JsonResponse({
        'is_authenticated': request.user.is_authenticated
    })

