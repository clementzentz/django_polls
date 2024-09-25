import datetime

from random import randrange

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from ..models import Question

class BaseTest(TestCase):
        
    def create_question(self, question_text, days, has_choices):
        time = timezone.now() + datetime.timedelta(days=days)
        question = Question.objects.create(
            question_text=question_text, pub_date=time)
        if has_choices:
            index = randrange(1, 9, 1)
            for i in range(index):
                question.choice_set.create(
                    choice_text=f"choice{i}", votes=0)
        return question

class IndexViewTests(BaseTest, TestCase):

    def test_no_questions(self):
        """ If no questions exist, an 
        appropriate message is displayed. """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [])

    def test_past_question_with_choices(self):
        """ Questions with a pub_date in the past
        and choices are displayed on the index page. """
        question = self.create_question(
            "Past question with choices.", (-30), True)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question])
    
    def test_past_question_without_choices(self):
        """ Questions with a pub_date in the past
        without choices are not displayed on the index page. """
        self.create_question(
            "Past question without choices.", (-30), False)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [])
    
    def test_future_question_with_choices(self):
        """ Questions with a pub_date in the future
         and choices are not displayed yet on the index page. """
        self.create_question(
            "Future question with choices.", 30, True)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [])
        
    def test_future_question_without_choices(self):
        """ Questions with a pub_date in the future
            and choices are not displayed yet on the index page. """
        self.create_question(
            "Future question without choices.", 30, False)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [])
    
    def test_future_and_past_question_with_choices(self):
        """ Even if both past and future questions exist, 
        only past questions whith are displayed. """
        past_question = self.create_question(
            "Past question with choices.", -30, True)
        self.create_question(
            "Future question with choices.", 30, True)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [past_question])

    def test_future_and_past_question_without_choices(self):
        """ Even if both past and future questions exist, 
        only past questions with choices are displayed. """
        self.create_question(
            "Past question with choices.", -30, False)
        self.create_question(
            "Future question with choices.", 30, False)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [])

    def test_two_past_questions_with_choices(self):
        """ The question index may display 
        multiple questions with choices. """
        question1 = self.create_question(
            "Past question 1 with choices.", -30, True)
        question2 = self.create_question(
            "Past question 2 with choices.", -5, True)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1])
        
    def test_two_past_questions_without_choices(self):
        """ The question index don't display 
        any questions without choices. """
        self.create_question(
            "Past question 1 with choices.", -30, False)
        self.create_question(
            "Past question 2 with choices.", -5, False)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [])
        
class DetailViewTests(BaseTest, TestCase): 

    def test_future_question_with_choices(self):
        """ The detail view of a question with a pub_date
        in the future returns a 404 not found. """
        future_question = self.create_question(
            "Future question with choices.", 5, True)
        url = reverse(
            "polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_with_choices(self):
        """ The detail view of a question with a pub_date
        in the past displays the question's text. """
        past_question = self.create_question(
            "Past Question with choices.", -5, True)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(
            response, past_question.question_text)
        
    def test_past_question_without_choices(self):
            """ The detail view of a question with a pub_date
            in the past displays the question's text. """
            past_question = self.create_question(
                "Past Question with choices.", -5, False)
            url = reverse("polls:detail", args=(past_question.id,))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)        
        
class ResultViewTests(BaseTest, TestCase):
    # "polls:results" is based on the url pattern name:
    # app_name="polls" urlpatterns = [
    # path("...", ..., name="results")]
    def test_future_question_with_choices(self):
        """ The detail view of a question with a pub_date
        in the future returns a 404 not found. """
        future_question = self.create_question(
            "Future question with choices.", 5, True)
        url = reverse(
            "polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_with_choices(self):
        past_question=self.create_question(
            "Past question with choices.", -10, True)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(
            response, past_question.question_text)
        
    def test_past_question_without_choices(self):
        past_question=self.create_question(
            "Past question with choices.", -10, False)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)        



