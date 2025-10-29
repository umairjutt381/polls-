from django.contrib import admin
from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    """Tabular Inline for Choice ,tabular is a html template"""

    model = Choice
    extra = 2                                     #show two extra blank forms

class QuestionAdmin(admin.ModelAdmin):
    """custom admin configuration,it means how to display views"""

    list_display = ('id', 'question_text', 'pub_date')
    search_fields = ('question_text',)
    ordering = ('-pub_date',)               #default sort in descending(-) order
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
