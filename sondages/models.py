from django.db import models
from django.contrib.auth.models import User
import uuid

# Extended profile for users (optional but useful)
class SurveyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_creator = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# Survey model
class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="surveys")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)  # <- Added deadline
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    password_protected = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True, null=True)
    share_token = models.OneToOneField("ShareToken", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

# Question model
QUESTION_TYPES = (
    ('SC', 'Single Choice'),
    ('MC', 'Multiple Choice'),
    ('TXT', 'Text'),
    ('SCL', 'Scale'),
)

class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.text

# Choice model
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text

# Token for sharing surveys
class ShareToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)

# Response from a user or anonymous
class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    respondent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

# Answer model
class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    text_answer = models.TextField(blank=True, null=True)
    scale_value = models.IntegerField(blank=True, null=True)
