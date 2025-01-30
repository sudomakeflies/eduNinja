from django.db import migrations, models
import django.db.models.deletion

def populate_question_order(apps, schema_editor):
    Evaluation = apps.get_model('evaluations', 'Evaluation')
    QuestionOrder = apps.get_model('evaluations', 'QuestionOrder')
    
    for evaluation in Evaluation.objects.all():
        # Obtener las preguntas en el orden actual
        for index, question in enumerate(evaluation.questions.all()):
            QuestionOrder.objects.create(
                evaluation=evaluation,
                question=question,
                order=index
            )

class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluations.evaluation')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluations.question')),
            ],
            options={
                'unique_together': {('evaluation', 'question')},
                'ordering': ['order'],
            },
        ),
        migrations.RunPython(populate_question_order, reverse_code=migrations.RunPython.noop),
    ]
