from django.shortcuts import render, redirect
from .forms import SondageForm
from django.contrib.auth.decorators import login_required
from .forms import QuestionForm, ChoiceFormSet
from .models import Sondage, Question, Choice, Reponse, Answer
from django.shortcuts import get_object_or_404
# Create your views here.


@login_required
def dashboard (request):
    my_sondages = Sondage.objects.filter(user=request.user)
    total_surveys = Sondage.objects.filter(user=request.user).count()  # Count surveys for the current user
    total_responses = Reponse.objects.filter(sondage__user=request.user).count()  # Count responses for the current user's surveys
      # Count active surveys for the current user

    return render(request, 'sondages/dashboard.html', {
        'my_sondages': my_sondages,
        'total_surveys': total_surveys,
        'total_responses': total_responses,
       
        })

@login_required
def add_question(request, sondage_id):
    sondage = Sondage.objects.get(id=sondage_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)

        if form.is_valid():
            question = form.save(commit=False)
            question.sondage = sondage
            question.save()
            

            formset = ChoiceFormSet(request.POST, instance=question)
            if formset.is_valid():
                formset.save()
                return redirect('dashboard')

            
    else:
        form = QuestionForm()
        formset = ChoiceFormSet(queryset=Choice.objects.none())

    return render(request, 'sondages/add_question.html', {'form': form, 'formset': formset, 'sondage': sondage})



@login_required
def create_sondage (request):
    if request.method == 'POST':
        form = SondageForm(request.POST)
        if form.is_valid():
            sondage = form.save(commit=False)
            sondage.user = request.user
            sondage.save()
            return redirect('add_question', sondage_id=sondage.id)  # redirige directement vers ajout de question

        
    else:
        form = SondageForm()
    return render(request, 'sondages/create_sondage.html', {'form': form})





def participer_sondage(request, sondage_id):
    sondage = get_object_or_404(Sondage, id=sondage_id)
    questions = sondage.questions.all()

    if request.method == 'POST':
        reponse = Reponse.objects.create(
            sondage=sondage,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR')
        )

        for question in questions:
            texte = request.POST.get(f"text_{question.id}", "")
            choix_ids = request.POST.getlist(f"choice_{question.id}")

            answer = Answer.objects.create(
                reponse=reponse,
                question=question,
                texte=texte if question.question_type == "tx" else None
            )
            if question.question_type in ["sc", "mc"]:
                answer.choix.set(choix_ids)
        return redirect('merci')  # page de confirmation

    return render(request, 'sondages/participer.html', {
        'sondage': sondage,
        'questions': questions,
    })


@login_required
def my_surveys(request):
    surveys = Sondage.objects.filter(user=request.user)
    return render(request, 'sondages/my_surveys.html', {'surveys': surveys})

@login_required
def survey_analytics(request):
    return render(request, 'sondages/survey_analytics.html', {'surveys': []})

@login_required
def survey_responses(request, survey_id=None):
    if survey_id:
        # Your survey responses logic here
        return render(request, 'sondages/survey_responses.html', {'survey_id': survey_id})
    else:
        return render(request, 'sondages/survey_responses.html', {'survey_id': None})
