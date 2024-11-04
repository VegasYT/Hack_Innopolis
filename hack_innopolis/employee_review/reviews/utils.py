import json
import re
import requests
from .models import Employee, GeneralSummary, AspectSummary, Aspect




def save_feedback_summary(employee_id, summary_text, psychotype_data):
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print("Сотрудник не найден.")
        return

    # Преобразуем summary_text в словарь, если это строка
    if isinstance(summary_text, str):
        try:
            summary_data = json.loads(summary_text)
        except json.JSONDecodeError as e:
            print("Ошибка декодирования JSON:", str(e))
            return
    else:
        summary_data = summary_text

    general_summary = summary_data.get('Вывод', {})
    general_score = general_summary.get('score', 0)
    general_description = general_summary.get('description', '')

    # Создаем общий обзор
    GeneralSummary.objects.create(
        employee=employee,
        text=general_description,
        score=general_score
    )

    # Обрабатываем и сохраняем сводки по аспектам
    for aspect_name, data in summary_data.items():
        if aspect_name == 'Вывод':
            continue
        
        score = data.get('score', 0)
        description = data.get('description', '')

        # Всегда создаем новый объект AspectSummary
        AspectSummary.objects.create(
            employee=employee,
            aspect_name=aspect_name,
            text=description,
            score=score
        )

    # Сохраняем психотип
    employee.psychotype = psychotype_data.get("psychotype", "Не определен")
    employee.psychotype_description = psychotype_data.get("psychotype_description", "Нет описания")
    employee.save()