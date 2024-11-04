from rest_framework import serializers
from .models import Feedback, ReviewCreator, Employee, Aspect



class AspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aspect
        fields = ['id', 'text']

    def create(self, validated_data):
        return Aspect.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance


class FeedbackSerializer(serializers.Serializer):
    ID_reviewer = serializers.IntegerField(required=False)
    ID_under_review = serializers.IntegerField(required=False)
    review = serializers.CharField()

    def validate(self, attrs):
        # Убираем пустые значения ID_reviewer и ID_under_review из атрибутов
        if 'ID_reviewer' in attrs and (attrs['ID_reviewer'] is None or attrs['ID_reviewer'] == ''):
            attrs.pop('ID_reviewer')  # Удаляем из атрибутов, если пустое

        if 'ID_under_review' in attrs and (attrs['ID_under_review'] is None or attrs['ID_under_review'] == ''):
            attrs.pop('ID_under_review')  # Удаляем из атрибутов, если пустое

        # Если оба поля отсутствуют, мы не можем создать отзыв
        if 'ID_reviewer' not in attrs and 'ID_under_review' not in attrs:
            raise serializers.ValidationError("Не указаны ID_reviewer или ID_under_review.")

        return attrs

    def create(self, validated_data):
        # Проверяем, что ID_reviewer и ID_under_review присутствуют
        reviewer_id = validated_data.get('ID_reviewer')
        employee_id = validated_data.get('ID_under_review')

        # Если ID_reviewer не указан, не создаем ReviewCreator
        if reviewer_id is not None:
            reviewer, _ = ReviewCreator.objects.get_or_create(id=reviewer_id)
        else:
            reviewer = None  # Или какое-то значение по умолчанию, если нужно

        # Если ID_under_review не указан, не создаем Employee
        if employee_id is not None:
            employee, _ = Employee.objects.get_or_create(id=employee_id)
        else:
            employee = None  # Или какое-то значение по умолчанию, если нужно

        # Проверяем, существует ли уже такой же отзыв
        if reviewer and employee:  # Проверяем, что оба объекта существуют
            existing_feedback = Feedback.objects.filter(
                text=validated_data['review'],
                employee=employee,
                review_creator=reviewer
            ).first()
            
            if existing_feedback:
                return existing_feedback  # Если отзыв уже существует, возвращаем его

        # Создаем новый отзыв только если есть employee и reviewer
        if employee and reviewer:
            feedback = Feedback(
                text=validated_data['review'],
                employee=employee,
                review_creator=reviewer
            )
            feedback.save()  # Сохраняем отзыв и рассчитываем вес
            return feedback

        return None  # Если отзыв не создан, возвращаем None
