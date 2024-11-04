import numpy as np
from textblob import TextBlob
from django.db import models
from django.core.exceptions import ValidationError



class Employee(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", null=True, blank=True)
    psychotype = models.CharField(max_length=10, blank=True, null=True)
    psychotype_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"Сотрудник {self.id}"


class Aspect(models.Model):
    id = models.BigAutoField(primary_key=True)
    text = models.TextField(verbose_name="Текст аспекта")

    class Meta:
        verbose_name = "Аспект"
        verbose_name_plural = "Аспекты"

    def __str__(self):
        return self.text


class ReviewCreator(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", null=True)

    class Meta:
        verbose_name = "Автор отзыва"
        verbose_name_plural = "Авторы отзывов"

    def __str__(self):
        return f"Автор отзыва {self.id}"


class Feedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    text = models.TextField(verbose_name="Текст отзыва")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    review_creator = models.ForeignKey(ReviewCreator, on_delete=models.CASCADE, verbose_name="Автор отзыва")
    is_self_review = models.BooleanField(default=False, verbose_name="Самооценка") 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", null=True)
    weight = models.FloatField(verbose_name="Вес отзыва", default=0.0)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def save(self, *args, **kwargs):
        # Сначала сохраняем, чтобы получить ID
        super().save(*args, **kwargs)  

        # Метод оценивания на основе стандартных отклонений
        std_weight = self.calculate_std_weight()

        # Установка начального веса
        self.weight = std_weight

        # Проверяем, является ли отзыв самооценкой
        self.is_self_review = (self.employee.id == self.review_creator.id)

        # Если это самооценка, вес 0
        if self.is_self_review:
            self.weight = 0
        
        # Анализируем эмоциональность
        emotion_weight = self.analyze_emotionality()

        # Корректируем вес на основе эмоциональности
        self.weight *= emotion_weight

        # Ограничиваем вес в пределах [0, 1]
        self.weight = max(0, min(self.weight, 1))
        
        # Проверка на допустимый диапазон значений веса
        if not 0 <= self.weight <= 1:
            raise ValidationError("Вес отзыва должен быть в диапазоне от 0 до 1.")

        # Сохраняем обновленный вес
        super().save(*args, **kwargs)

    def analyze_emotionality(self):
        # Используем TextBlob для анализа эмоциональности
        analysis = TextBlob(self.text)

        # Получаем полярность (от -1 до 1)
        polarity = analysis.sentiment.polarity

        # Корректируем вес в зависимости от полярности
        # Чем ближе к 0, тем больше вес
        emotional_weight = 1 - abs(polarity)

        return emotional_weight

    def calculate_std_weight(self):
        # Получаем все отзывы для данного сотрудника
        feedbacks = Feedback.objects.filter(employee=self.employee)
        
        if feedbacks.count() < 2:
            return 1.0  # Если отзывов недостаточно, возвращаем максимальный вес

        # Предположим, что вес каждого отзыва - это его длина (можно использовать другую метрику)
        weights = [len(fb.text) for fb in feedbacks]
        
        # Вычисляем стандартное отклонение
        std_dev = np.std(weights)

        # Преобразуем стандартное отклонение в вес
        weight = 1 - std_dev / max(weights)  # Нормализуем на максимальную длину
        return max(0, min(weight, 1))

    def __str__(self):
        return f"Отзыв от {self.review_creator.id} к {self.employee.id} с весом {self.weight}"

 
class GeneralSummary(models.Model):
    id = models.BigAutoField(primary_key=True)
    text = models.TextField(verbose_name="Общий вывод")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    score = models.FloatField(verbose_name="Общая оценка", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", null=True) 

    class Meta:
        verbose_name = "Общий вывод"
        verbose_name_plural = "Общие выводы"

    def __str__(self):
        return f"Общий вывод для сотрудника {self.employee.id}" 


class AspectSummary(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    aspect_name = models.CharField(max_length=255, verbose_name="Название аспекта", default="Unnamed Aspect")
    text = models.TextField(verbose_name="Текст аспекта")
    score = models.FloatField(verbose_name="Оценка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", null=True)

    class Meta:
        verbose_name = "Вывод по аспекту" 
        verbose_name_plural = "Выводы по аспектам"

    def __str__(self):
        return f"Аспект {self.aspect_name} - Оценка: {self.score}"
 