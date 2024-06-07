# Generated by Django 3.2.25 on 2024-06-06 14:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0013_alter_question_latex_format'),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('is_latex', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='answer',
            name='submission_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='date',
            field=models.DateField(db_index=True, default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='period',
            field=models.CharField(db_index=True, default=1, max_length=10),
        ),
        migrations.AlterField(
            model_name='question',
            name='difficulty',
            field=models.CharField(choices=[('Easy', 'Fácil'), ('Medium', 'Medio'), ('Hard', 'Difícil')], db_index=True, max_length=50),
        ),
        migrations.RemoveField(
            model_name='question',
            name='options',
        ),
        migrations.AlterField(
            model_name='question',
            name='subject',
            field=models.CharField(choices=[('Math_Algebra', 'Matemáticas - Álgebra'), ('Math_Statistics', 'Matemáticas - Estadística'), ('Math_Geometry', 'Matemáticas - Geometría'), ('Math_Calculus', 'Matemáticas - Cálculo'), ('Math_Trigonometry', 'Matemáticas - Trigonometría'), ('Math_Probability', 'Matemáticas - Probabilidad'), ('Math_Number Theory', 'Matemáticas - Teoría de Números'), ('Math_Logic', 'Matemáticas - Lógica'), ('Math_Graphics', 'Matemáticas - Gráficos'), ('Math_Tables', 'Matemáticas - Tablas'), ('Physics_Kinematics', 'Física - Cinemática'), ('Physics_Waves', 'Física - Ondas'), ('Physics_Thermodynamics', 'Física - Termodinámica'), ('Physics_Electromagnetism', 'Física - Electromagnetismo'), ('Physics_Optics', 'Física - Óptica'), ('Physics_Mechanics', 'Física - Mecánica'), ('Physics_Acoustics', 'Física - Acústica'), ('Physics_Astronomy', 'Física - Astronomía'), ('Physics_Nuclear Physics', 'Física - Física Nuclear'), ('Physics_Relativity', 'Física - Relatividad'), ('Physics_Particle Physics', 'Física - Física de Partículas'), ('Physics_Dynamics', 'Física - Dinámica'), ('Physics_Energy', 'Física - Energía')], db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name='question',
            name='options',
            field=models.ManyToManyField(to='evaluations.Option'),
        ),
    ]