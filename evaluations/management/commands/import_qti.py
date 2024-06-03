# management/commands/import_qti.py
import os
from django.core.management.base import BaseCommand, CommandError
from evaluations.utils import parse_qti_directory

class Command(BaseCommand):
    help = 'Import QTI questions from a directory'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='The directory containing the QTI files')

    def handle(self, *args, **kwargs):
        directory = kwargs['directory']

        # Verificar la existencia del directorio
        if not os.path.isdir(directory):
            raise CommandError(f"Directory '{directory}' does not exist")

        try:
            parse_qti_directory(directory)
            self.stdout.write(self.style.SUCCESS('Successfully imported QTI questions'))
        except Exception as e:
            raise CommandError(f"Failed to import QTI questions: {e}")
