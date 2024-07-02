# evaluation/serializers.py
from rest_framework import serializers
from .models import Course, Option, Question, Evaluation, Answer

class CourseSerializer(serializers.ModelSerializer):
    evaluations = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_evaluations(self, obj):
        request = self.context.get('request')
        evaluations = obj.evaluation_set.all()
        return [
            {
                'id': evaluation.pk,
                'name': evaluation.name,
                'url': request.build_absolute_uri(f"/api/take_evaluation/{evaluation.pk}")
            }
            for evaluation in evaluations
        ]
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Evaluation
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

