import os
import json
from django.core.management.base import BaseCommand, CommandError
from evaluations.models import Evaluation
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    help = 'Grade JSON submissions for a specific evaluation'

    def add_arguments(self, parser):
        parser.add_argument('evaluation_id', type=int, help='ID of the evaluation')
        parser.add_argument('folder_path', type=str, help='Path to folder containing JSON submissions')

    def handle(self, *args, **options):
        evaluation_id = options['evaluation_id']
        folder_path = options['folder_path']

        # Validate and get evaluation
        try:
            evaluation = Evaluation.objects.get(pk=evaluation_id)
        except ObjectDoesNotExist:
            raise CommandError(f'Evaluation with ID {evaluation_id} does not exist')

        # Validate folder path
        if not os.path.isdir(folder_path):
            raise CommandError(f'Folder path {folder_path} does not exist or is not a directory')

        # Get ordered questions for evaluation
        ordered_questions = Evaluation.get_ordered_questions(evaluation)
        questions_count = ordered_questions.count()
        
        # Process each JSON file in the folder
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
        
        if not json_files:
            self.stdout.write(self.style.WARNING('No JSON files found in the specified folder'))
            return

        for json_file in json_files:
            file_path = os.path.join(folder_path, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    submission = json.load(f)
                
                # Extract student name and answers
                student_name = submission.get('nombre', 'No identificado')
                answers = submission.get('respuestas', {})
                
                self.stdout.write('\n' + '=' * 50)
                self.stdout.write(f'Student: {student_name}')
                self.stdout.write('Question Results:')
                
                # Calculate score
                correct_count = 0
                for i, question in enumerate(ordered_questions, 1):
                    # Get student's answer, converting key to string since JSON keys are strings
                    student_answer = answers.get(str(i))
                    # Strip 'choice' prefix from correct answer
                    correct_answer = question.correct_answer.lower().replace('choice', '')
                    
                    # Validate and compare answer
                    if student_answer is None:
                        result = '✗ No answer provided'
                        status = self.style.ERROR(result)
                    elif not isinstance(student_answer, str) or student_answer.lower() not in ['a', 'b', 'c', 'd']:
                        result = f'✗ Invalid answer (selected: {student_answer})'
                        status = self.style.ERROR(result)
                    else:
                        student_answer = student_answer.lower()
                        if student_answer == correct_answer:
                            result = f'✓ Correct (selected: {student_answer})'
                            status = self.style.SUCCESS(result)
                            correct_count += 1
                        else:
                            result = f'✗ Incorrect (selected: {student_answer}, correct: {correct_answer})'
                            status = self.style.ERROR(result)
                    
                    self.stdout.write(f'{i}. {status}')
                
                # Calculate and display final score
                # Convert to float to handle decimal multiplication
                max_score = float(evaluation.max_score)
                score = (correct_count / questions_count) * max_score
                self.stdout.write(f'\nFinal Score: {score:.2f}/{evaluation.max_score}')
                self.stdout.write(f'Correct Answers: {correct_count}/{questions_count}')

            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f'Error: Invalid JSON format in file {json_file}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing file {json_file}: {str(e)}'))

        self.stdout.write('\nGrading completed.')
