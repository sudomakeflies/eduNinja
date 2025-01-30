# competencies/management/commands/load_competencies.py
from django.core.management.base import BaseCommand
from django.db import transaction
from personalized_learning.models import Competency
import json

class Command(BaseCommand):
    help = 'Carga las competencias desde un archivo JSON'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Ruta al archivo JSON de competencias')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todas las competencias existentes antes de cargar las nuevas',
        )

    def load_competencies(self, competency_data, parent=None):
        """
        Carga recursivamente las competencias y sus sub-competencias
        """
        competency = Competency.objects.create(
            name=competency_data['name'],
            description=competency_data['description'],
            parent=parent
        )
        
        # Procesa las sub-competencias si existen
        if 'sub_competencies' in competency_data:
            for sub_comp_data in competency_data['sub_competencies']:
                self.load_competencies(sub_comp_data, parent=competency)
        
        return competency

    def handle(self, *args, **options):
        json_file = options['json_file']
        
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'No se pudo encontrar el archivo: {json_file}'))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR('El archivo JSON no es válido'))
            return

        # Usar transacción para asegurar la integridad de los datos
        with transaction.atomic():
            if options['clear']:
                self.stdout.write('Eliminando competencias existentes...')
                Competency.objects.all().delete()

            try:
                for competency_data in data['competencies']:
                    self.load_competencies(competency_data)
                self.stdout.write(self.style.SUCCESS('Competencias cargadas exitosamente'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error al cargar las competencias: {str(e)}'))
                # La transacción se revertirá automáticamente si hay un error
