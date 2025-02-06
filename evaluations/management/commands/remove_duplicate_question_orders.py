from django.core.management.base import BaseCommand
from evaluations.models import Evaluation, QuestionOrder

class Command(BaseCommand):
    help = 'Removes duplicate QuestionOrder entries for each evaluation'

    def handle(self, *args, **options):
        for evaluation in Evaluation.objects.all():
            self.stdout.write(self.style.SUCCESS(f'Processing evaluation: {evaluation.name} (ID: {evaluation.id})'))
            question_ids = []
            for question_order in QuestionOrder.objects.filter(evaluation=evaluation).order_by('order'):
                if question_order.question_id in question_ids:
                    self.stdout.write(self.style.WARNING(f'  Deleting duplicate QuestionOrder: {question_order}'))
                    question_order.delete()
                else:
                    question_ids.append(question_order.question_id)
            self.stdout.write(self.style.SUCCESS(f'  Finished processing evaluation: {evaluation.name} (ID: {evaluation.id})'))
