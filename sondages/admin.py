from django.contrib import admin
from .models import Sondage, Question, Choice 
# Register your models here.


admin.site.register(Sondage)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)