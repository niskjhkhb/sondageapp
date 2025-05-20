from django.db import transaction
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from sondages.models import Survey, Question, Answer, Choice
from sondages.forms import SurveyForm, QuestionForm, OptionForm, AnswerForm, BaseAnswerFormSet


@login_required
def survey_list(request):
    """User can view all their surveys"""
    surveys = Survey.objects.filter(creator=request.user).order_by("-created_at").all()
    return render(request, "survey/list.html", {"surveys": surveys})


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
    num_submissions = survey.submission_set.filter(is_complete=True).count()
    return render(
        request,
        "survey/detail.html",
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

    return render(request, "survey/create.html", {"form": form})


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
        return render(request, "survey/edit.html", {"survey": survey, "questions": questions})


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

    return render(request, "survey/question.html", {"survey": survey, "form": form})


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
        "survey/options.html",
        {"survey": survey, "question": question, "options": options, "form": form},
    )


def start(request, pk):
    """Survey-taker can start a survey"""
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    if request.method == "POST":
        sub = Submission.objects.create(survey=survey)
        return redirect("survey-submit", survey_pk=pk, sub_pk=sub.pk)

    return render(request, "survey/start.html", {"survey": survey})


def submit(request, survey_pk, sub_pk):
    """Survey-taker submit their completed survey."""
    try:
        survey = Survey.objects.prefetch_related("question_set__option_set").get(
            pk=survey_pk, is_active=True
        )
    except Survey.DoesNotExist:
        raise Http404()

    try:
        sub = survey.submission_set.get(pk=sub_pk, is_complete=False)
    except Submission.DoesNotExist:
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
                        option_id=form.cleaned_data["option"], submission_id=sub_pk,
                    )

                sub.is_complete = True
                sub.save()
            return redirect("survey-thanks", pk=survey_pk)

    else:
        formset = AnswerFormSet(form_kwargs=form_kwargs)

    question_forms = zip(questions, formset)
    return render(
        request,
        "survey/submit.html",
        {"survey": survey, "question_forms": question_forms, "formset": formset},
    )


def thanks(request, pk):
    """Survey-taker receives a thank-you message."""
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    return render(request, "survey/thanks.html", {"survey": survey})


@login_required
def dashboard(request):
    """User can view their dashboard with survey stats"""
    total_surveys = Survey.objects.filter(creator=request.user).count()
    total_responses = Answer.objects.filter(submission__survey__creator=request.user).count()
    active_surveys = Survey.objects.filter(creator=request.user, is_active=True).count()

    context = {
        "total_surveys": total_surveys,
        "total_responses": total_responses,
        "active_surveys": active_surveys,
    }
    return render(request, "sondages/dashboard.html", context)


@login_required
def settings(request):
    """Handle user settings page"""
    if request.method == 'POST':
        # Handle form submission
        user = request.user
        profile = user.profile

        # Update profile picture if provided
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        # Update display name
        if 'display_name' in request.POST:
            user.username = request.POST['display_name']

        # Update bio
        if 'bio' in request.POST:
            profile.bio = request.POST['bio']

        # Update email
        if 'email' in request.POST:
            user.email = request.POST['email']

        # Update password if provided
        if 'current_password' in request.POST and 'new_password' in request.POST:
            if user.check_password(request.POST['current_password']):
                user.set_password(request.POST['new_password'])
            else:
                messages.error(request, 'Current password is incorrect')
                return redirect('settings')

        # Update notification preferences
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.survey_notifications = request.POST.get('survey_notifications') == 'on'
        profile.marketing_notifications = request.POST.get('marketing_notifications') == 'on'

        # Update survey defaults
        profile.default_language = request.POST.get('default_language', 'en')
        profile.response_anonymous = request.POST.get('response_anonymous') == 'on'

        # Save changes
        user.save()
        profile.save()

        messages.success(request, 'Settings updated successfully')
        return redirect('settings')

    # For GET request, display the settings page with current values
    context = {
        'user': request.user,
        'profile': request.user.profile
    }
    return render(request, 'settings.html', context)


@login_required
def create_survey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.creator = request.user
            survey.save()
            messages.success(request, 'Survey created successfully!')
            return redirect('dashboard')
    else:
        form = SurveyForm()
    
    return render(request, 'sondages/create_survey.html', {'form': form})


@login_required
def create_text_survey(request):
    """Create a text-based survey"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        survey = Survey.objects.create(
            title=title,
            description=description,
            creator=request.user
        )
        
        questions = request.POST.getlist('questions[]')
        for i, question_text in enumerate(questions):
            Question.objects.create(
                survey=survey,
                text=question_text,
                question_type='TXT',
                order=i+1
            )
        
        return JsonResponse({'success': True, 'survey_id': survey.id})
    
    return render(request, "sondages/create_text_survey.html")


@login_required
def create_qcm_survey(request):
    """Create a multiple choice survey"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        survey = Survey.objects.create(
            title=title,
            description=description,
            creator=request.user
        )
        
        questions = request.POST.getlist('questions[]')
        choices = request.POST.getlist('choices[]')
        
        for i, question_text in enumerate(questions):
            question = Question.objects.create(
                survey=survey,
                text=question_text,
                question_type='MC',
                order=i+1
            )
            
            # Create choices for this question
            question_choices = choices[i].split(',') if i < len(choices) else []
            for choice in question_choices:
                Choice.objects.create(
                    question=question,
                    text=choice.strip()
                )
        
        return JsonResponse({'success': True, 'survey_id': survey.id})
    
    return render(request, "sondages/create_qcm_survey.html")


@login_required
def create_scale_survey(request):
    """Create a scale-based survey"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        survey = Survey.objects.create(
            title=title,
            description=description,
            creator=request.user
        )
        
        questions = request.POST.getlist('questions[]')
        min_values = request.POST.getlist('min_values[]')
        max_values = request.POST.getlist('max_values[]')
        
        for i, question_text in enumerate(questions):
            Question.objects.create(
                survey=survey,
                text=question_text,
                question_type='SCL',
                order=i+1,
                min_value=min_values[i] if i < len(min_values) else 1,
                max_value=max_values[i] if i < len(max_values) else 5
            )
        
        return JsonResponse({'success': True, 'survey_id': survey.id})
    
    return render(request, "sondages/create_scale_survey.html")


@login_required
def create_qcu_survey(request):
    """Create a single choice survey (QCU)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        survey = Survey.objects.create(
            title=title,
            description=description,
            creator=request.user
        )
        
        questions = request.POST.getlist('questions[]')
        choices = request.POST.getlist('choices[]')
        
        for i, question_text in enumerate(questions):
            question = Question.objects.create(
                survey=survey,
                text=question_text,
                question_type='SC',  # Single Choice
                order=i+1
            )
            
            # Create choices for this question
            question_choices = choices[i].split(',') if i < len(choices) else []
            for choice in question_choices:
                Choice.objects.create(
                    question=question,
                    text=choice.strip()
                )
        
        return JsonResponse({'success': True, 'survey_id': survey.id})
    
    return render(request, "sondages/create_qcu_survey.html")

