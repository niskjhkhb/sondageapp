from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Sondage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    background_color = models.CharField(max_length=7, default="#ffffff")
    font_family = models.CharField(max_length=100, default="Poppins")
    

    def __str__(self):
        return self.title



class Question(models.Model):
    QUESTION_TYPES = [
        ('sc', 'Single Choice'),
        ('mc', 'Multiple Choice'),
        ('tx', 'Text'),
        ('scal','echelle (1-5)'),
    ]

    sondage = models.ForeignKey(Sondage, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=200)
    question_type = models.CharField(max_length=4, choices=QUESTION_TYPES)
    
    required = models.BooleanField(default=True) #la question est elle obligatoire?

    def __str__(self):
        return self.text
    


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    
    def __str__(self):
        return self.text
    


class Reponse(models.Model):
    sondage = models.ForeignKey(Sondage, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

class Answer(models.Model):
    reponse = models.ForeignKey(Reponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choix = models.ManyToManyField(Choice, blank=True)  # Pour choix multiples
    texte = models.TextField(blank=True, null=True)      # Pour réponses libres
