from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question

class QuestionQuerySetMixin:
    def get_queryset(self):
        """ Excludes any questions 
        that aren't published yet. """
        return (Question.objects
                .exclude(choice__isnull=True)
                .filter(pub_date__lte=timezone.now()))

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(
            pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request,"polls/detail.html", {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(
            reverse("polls:results", args=(question.id,)))

# IndexView inherit QuestionQuerySetMixin
class IndexView(QuestionQuerySetMixin, generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    def get_queryset(self):
        """Return the last five published questions.
        (not including those set to be published in the future)"""
        return (super().get_queryset()
                .order_by("-pub_date")[:5])
    
# DetailView inherit QuestionQuerySetMixin  
class DetailView(QuestionQuerySetMixin, generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

# ResultsView inherit QuestionQuerySetMixin 
class ResultsView(QuestionQuerySetMixin, generic.DetailView):
    model = Question
    template_name = "polls/results.html"