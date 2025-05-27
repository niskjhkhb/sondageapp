from django.shortcuts import render, redirect, get_object_or_404
from .forms import SondageForm, QuestionForm, ChoiceFormSet  # Added ChoiceForm
from django.contrib.auth.decorators import login_required
from .models import Sondage, Question, Choice, Reponse, Answer
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse

@login_required
def dashboard(request):
    my_sondages = Sondage.objects.filter(user=request.user)
    total_surveys = Sondage.objects.filter(user=request.user).count()
    total_responses = Reponse.objects.filter(sondage__user=request.user).count()

    return render(request, 'sondages/dashboard.html', {
        'my_sondages': my_sondages,
        'total_surveys': total_surveys,
        'total_responses': total_responses,
    })

@login_required
def add_question(request, sondage_id):
    sondage = get_object_or_404(Sondage, id=sondage_id)

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
def create_sondage(request):
    if request.method == 'POST':
        form = SondageForm(request.POST)
        if form.is_valid():
            sondage = form.save(commit=False)
            sondage.user = request.user
            sondage.save()
            return redirect('add_question', sondage_id=sondage.id)
    else:
        form = SondageForm()
    return render(request, 'sondages/create_sondage.html', {'form': form})


from django.shortcuts import render, redirect, get_object_or_404
from .forms import SondageForm, QuestionForm, ChoiceFormSet  # Added ChoiceForm
from django.contrib.auth.decorators import login_required
from .models import Sondage, Question, Choice, Reponse, Answer
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone

def participer_sondage(request, sondage_id):
    sondage = get_object_or_404(Sondage, shareable_link=sondage_id)
    questions = sondage.questions.all()
    ip_address = request.META.get('REMOTE_ADDR')

    if sondage.limit_ip and Reponse.objects.filter(sondage=sondage, ip_address=ip_address).exists():
        return HttpResponse("You have already submitted this survey from this IP address.")

    if request.method == 'POST':
        reponse = Reponse.objects.create(
            sondage=sondage,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address
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
        return redirect('merci')
    print(f"sondage.shareable_link: {sondage.shareable_link}")  # Add this line
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


def QCM(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            return redirect('dashboard')
    else:
        form = QuestionForm()
    return render(request, 'sondages/QCM.html', {'form': form})

def QCU(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            return redirect('dashboard')
    else:
        form = QuestionForm()
    return render(request, 'sondages/QCU.html', {'form': form})

def TEXT(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            return redirect('dashboard')
    else:
        form = QuestionForm()
    return render(request, 'sondages/TEXT.html', {'form': form})

def SCALE(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            return redirect('dashboard')
    else:
        form = QuestionForm()
    return render(request, 'sondages/SCALE.html', {'form': form})

def mixed(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            return redirect('dashboard')
    else:
        form = QuestionForm()
    return render(request, 'sondages/mixed.html', {'form': form})



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Sondage, Question


@csrf_exempt  # Be careful with this in production
def save_scale_sondage(request):
    if request.method == 'POST':
        
        try:
            data = json.loads(request.body.decode('utf-8'))
            survey_title = data.get('surveyTitle')
            survey_description = data.get('surveyDescription')
            questions = data.get('questions')

            # Create Sondage object
            sondage = Sondage.objects.create(
                title=survey_title,
                description=survey_description,
                user=request.user  # Assuming the user is logged in
            )

            # Create Question objects
            for question_data in questions:
                question = Question.objects.create(
                   sondage=sondage,
                   text=question_data.get('questionText'),
                   question_type='scal',
                   min_value=question_data.get('minValue'),
                   max_value=question_data.get('maxValue')
                )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print("Error:", e)  # Print the error message
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    
  
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Sondage, Question, Choice

@csrf_exempt  # Be careful with this in production
def save_qcu_sondage(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            survey_title = data.get('surveyTitle')
            survey_description = data.get('surveyDescription')
            questions = data.get('questions')

            # Create Sondage object
            sondage = Sondage.objects.create(
                title=survey_title,
                description=survey_description,
                user=request.user  # Assuming the user is logged in
            )

            # Create Question objects
            for question_data in questions:
                question = Question.objects.create(
                    sondage=sondage,
                    text=question_data.get('questionText'),
                    question_type='qcu'  # Set question type to 'qcu'
                )

                # Create Choice objects
                options = question_data.get('options')
                for option_text in options:
                    Choice.objects.create(
                        question=question,
                        text=option_text
                    )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print("Error:", e)  # Print the error message
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
        views.py
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    import json
    from .models import Sondage, Question, Choice
    
    
    
    
    
    
@csrf_exempt  # Be careful with this in production
def save_qcm_sondage(request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode('utf-8'))
                survey_title = data.get('surveyTitle')
                survey_description = data.get('surveyDescription')
                questions = data.get('questions')
    
                # Create Sondage object
                sondage = Sondage.objects.create(
                    title=survey_title,
                    description=survey_description,
                    user=request.user  # Assuming the user is logged in
                )
    
                # Create Question objects
                for question_data in questions:
                    question = Question.objects.create(
                        sondage=sondage,
                        text=question_data.get('questionText'),
                        question_type='qcm'  # Set question type to 'qcm'
                    )
    
                    # Create Choice objects
                    options = question_data.get('options')
                    for option_text in options:
                        Choice.objects.create(
                            question=question,
                            text=option_text
                        )
    
                return JsonResponse({'status': 'success'})
    
            except Exception as e:
                print("Error:", e)  # Print the error message
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
        
        

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Sondage, Question

@csrf_exempt  # Be careful with this in production
def save_text_sondage(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            survey_title = data.get('surveyTitle')
            survey_description = data.get('surveyDescription')
            questions = data.get('questions')

            # Create Sondage object
            sondage = Sondage.objects.create(
                title=survey_title,
                description=survey_description,
                user=request.user  # Assuming the user is logged in
            )

            # Create Question objects
            for question_data in questions:
                question = Question.objects.create(
                    sondage=sondage,
                    text=question_data.get('questionText'),
                    question_type='text',  # Set question type to 'text'
                    required=question_data.get('required'),
                    min_value=question_data.get('minLength'),
                    max_value=question_data.get('maxLength')
                )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print("Error:", e)  # Print the error message
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Sondage, Question, Choice

@csrf_exempt  # Be careful with this in production
def save_mixed_sondage(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            survey_title = data.get('surveyTitle')
            survey_description = data.get('surveyDescription')
            questions = data.get('questions')

            # Create Sondage object
            sondage = Sondage.objects.create(
                title=survey_title,
                description=survey_description,
                user=request.user  # Assuming the user is logged in
            )

            # Create Question objects
            for question_data in questions:
                question_text = question_data.get('questionText')
                question_type = question_data.get('questionType')
                question = Question.objects.create(
                    sondage=sondage,
                    text=question_text,
                    question_type=question_type
                )

                # Create Choice objects if the question type is QCU or QCM
                if question_type in ['qcu', 'qcm']:
                    options = question_data.get('options')
                    for option_text in options:
                        Choice.objects.create(
                            question=question,
                            text=option_text
                        )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print("Error:", e)  # Print the error message
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    

@login_required
def update_sondage(request, sondage_id):
    sondage = get_object_or_404(Sondage, pk=sondage_id, user=request.user)
    if request.method == 'POST':
        sondage.title = request.POST['title']
        sondage.description = request.POST['description']
        sondage.password = request.POST.get('password', '')  # Handle optional password
        sondage.limit_responses = request.POST.get('limit_responses', False) == 'on'
        sondage.limit_ip = request.POST.get('limit_ip', False) == 'on'
        sondage.save()
        return redirect('survey_details', sondage_id=sondage.id)
    return render(request, 'sondages/update_sondage.html', {'sondage': sondage})

@login_required
def delete_sondage(request, sondage_id):
    sondage = get_object_or_404(Sondage, pk=sondage_id, user=request.user)
    if request.method == 'POST':
        sondage.delete()
        return redirect('dashboard')
    return render(request, 'sondages/delete_sondage.html', {'sondage': sondage})



def survey_details(request, sondage_id):
    sondage = get_object_or_404(Sondage, pk=sondage_id, user=request.user)
    shareable_link = request.build_absolute_uri(reverse('participer_sondage', args=[sondage.shareable_link]))
    embed_code = format_html('<iframe src="{}" width="600" height="400"></iframe>', shareable_link)

    return render(request, 'sondages/survey_details.html', {
        'sondage': sondage,
        'shareable_link': shareable_link,
        'embed_code': embed_code,
    })


import json
from django.shortcuts import render, get_object_or_404
from .models import Sondage, Question, Answer, Choice

from django.shortcuts import render, get_object_or_404
from .models import Sondage, Question, Answer, Choice
from .forms import FilterForm  # Import the FilterForm

from django.shortcuts import render, get_object_or_404
from .models import Sondage, Answer, Question, Choice
from collections import Counter

import json
from django.shortcuts import render, get_object_or_404
from .models import Sondage, Question, Answer, Choice
from .forms import FilterForm  # Import the FilterForm

def apply_filters(responses, user, date):
    if user:
        responses = responses.filter(user__username__icontains=user)
    if date:
        responses = responses.filter(date__date=date)
    return responses

def survey_results(request, sondage_id):
    sondage = get_object_or_404(Sondage, id=sondage_id)
    questions = sondage.questions.all()
    num_responses = sondage.reponse_set.count()

    # Apply filters
    form = FilterForm(request.GET)
    responses = sondage.reponse_set.all()  # Start with all responses
    if form.is_valid():
        user = form.cleaned_data.get('user')
        date = form.cleaned_data.get('date')
        responses = apply_filters(responses, user, date)

    chart_data = []

    for question in questions:
        data_entry = {
            'question_text': question.text,
            'chart_type': '',
            'labels': [],
            'values': [],
            'responses': [],
        }

        if question.question_type in ['sc', 'mc']:
            labels = [choice.text for choice in question.choices.all()]
            values = []

            for choice in question.choices.all():
                count = Answer.objects.filter(question=question, choix=choice, reponse__in=responses).count()
                values.append(count)

            data_entry['chart_type'] = 'pie' if question.question_type == 'sc' else 'bar'
            data_entry['labels'] = labels
            data_entry['values'] = values

        elif question.question_type == 'scal':
            labels = [str(i) for i in range(question.min_value, question.max_value + 1)]
            values = []

            for i in range(question.min_value, question.max_value + 1):
                count = Answer.objects.filter(question=question, texte=str(i), reponse__in=responses).count()
                values.append(count)

            data_entry['chart_type'] = 'bar'
            data_entry['labels'] = labels
            data_entry['values'] = values

        elif question.question_type == 'tx':
            text_responses = [answer.texte for answer in Answer.objects.filter(question=question, reponse__in=responses) if answer.texte]
            data_entry['chart_type'] = 'text'
            data_entry['responses'] = text_responses

        chart_data.append(data_entry)

    return render(request, 'sondages/survey_results.html', {
        'sondage': sondage,
        'num_responses': num_responses,
        'chart_data': chart_data,
        'filter_form': form,  # Pass the form to the template
    })


import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Sondage, Reponse, Answer


def export_responses(request, sondage_id):
    sondage = get_object_or_404(Sondage, pk=sondage_id)
    responses = Reponse.objects.filter(sondage=sondage)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{sondage.title}_responses.csv"'

    writer = csv.writer(response)

    # Write header row
    header = ['Date', 'User', 'IP Address'] + [q.text for q in sondage.questions.all()]
    writer.writerow(header)

    # Write data rows
    for r in responses:
        row = [r.date, r.user, r.ip_address]
        for q in sondage.questions.all():
            try:
                answer = Answer.objects.get(reponse=r, question=q)
                if q.question_type in ['sc', 'mc']:
                    choices = ", ".join([c.text for c in answer.choix.all()])
                    row.append(choices)
                else:
                    row.append(answer.texte or '')
            except Answer.DoesNotExist:
                row.append('')
        writer.writerow(row)

    return response


import xlsxwriter
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Sondage, Reponse, Answer

def export_responses_excel(request, sondage_id):
    sondage = get_object_or_404(Sondage, pk=sondage_id)
    responses = Reponse.objects.filter(sondage=sondage)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{sondage.title}_responses.xlsx"'

    workbook = xlsxwriter.Workbook(response, {'remove_timezone': True})
    worksheet = workbook.add_worksheet()

    # Write header row
    header = ['Date', 'User', 'IP Address'] + [q.text for q in sondage.questions.all()]
    for col_num, column_title in enumerate(header):
        worksheet.write(0, col_num, column_title)

    # Write data rows
    for row_num, r in enumerate(responses, 1):
        row = [str(r.date), str(r.user), r.ip_address or '']
        for q in sondage.questions.all():
            try:
                answer = Answer.objects.get(reponse=r, question=q)
                if q.question_type in ['sc', 'mc']:
                    choices = ", ".join([c.text for c in answer.choix.all()])
                    row.append(choices)
                else:
                    row.append(answer.texte or '')
            except Answer.DoesNotExist:
                row.append('')
        for col_num, cell_value in enumerate(row):
            worksheet.write(row_num + 1, col_num, cell_value)

    workbook.close()
    return response

