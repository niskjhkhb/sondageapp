from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Sondage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    primary_color = models.CharField(max_length=7, default="#4F46E5")
    background_color = models.CharField(max_length=7, default="#ffffff")
    font_family = models.CharField(max_length=100, default="Poppins")
    shareable_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    limit_responses = models.BooleanField(default=False)
    limit_ip = models.BooleanField(default=True)

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
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.text
    
    @property
    def scale_range(self):
        if self.question_type == 'scal' and self.min_value is not None and self.max_value is not None:
            return range(self.min_value, self.max_value + 1)
        return []


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
    answer = models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(default=timezone.now)  # Modified line

class Answer(models.Model):
    reponse = models.ForeignKey(Reponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choix = models.ManyToManyField(Choice, blank=True)  # Pour choix multiples
    texte = models.TextField(blank=True, null=True)      # Pour réponses libres