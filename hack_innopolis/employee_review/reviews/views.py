import re
import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import Employee, Feedback, GeneralSummary, AspectSummary, Aspect
from .serializers import FeedbackSerializer, AspectSerializer
from .utils import save_feedback_summary



class AspectView(generics.ListCreateAPIView):
    queryset = Aspect.objects.all()
    serializer_class = AspectSerializer


class AspectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Aspect.objects.all()
    serializer_class = AspectSerializer


class FeedbackByEmployeeView(APIView):
    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Сотрудник не найден."}, status=status.HTTP_404_NOT_FOUND)

        feedbacks = Feedback.objects.filter(employee=employee)
        serialized_feedbacks = [
            {
                "ID_reviewer": feedback.review_creator.id,
                "ID_under_review": feedback.employee.id,
                "review": feedback.text,
                "weight": feedback.weight,
                "is_self_review": feedback.is_self_review
            }
            for feedback in feedbacks
        ]
        
        return Response(serialized_feedbacks, status=status.HTTP_200_OK)
    

class AspectSummaryByEmployeeView(APIView):
    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Сотрудник не найден."}, status=status.HTTP_404_NOT_FOUND)

        aspect_summaries = AspectSummary.objects.filter(employee=employee)
        serialized_aspect_summaries = [
            {
                "aspect_name": aspect_summary.aspect_name,
                "text": aspect_summary.text,
                "score": aspect_summary.score,
                "created_at": aspect_summary.created_at
            }
            for aspect_summary in aspect_summaries
        ]
        
        return Response(serialized_aspect_summaries, status=status.HTTP_200_OK)


class GeneralSummaryByEmployeeView(APIView):
    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Сотрудник не найден."}, status=status.HTTP_404_NOT_FOUND)

        general_summaries = GeneralSummary.objects.filter(employee=employee)
        serialized_general_summaries = [
            {
                "text": general_summary.text,
                "score": general_summary.score,
                "created_at": general_summary.created_at
            }
            for general_summary in general_summaries
        ]
        
        return Response(serialized_general_summaries, status=status.HTTP_200_OK)
    

class EmployeePsychotypeView(APIView):
    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Сотрудник не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Сериализуем данные о психотипе
        psychotype_data = {
            "psychotype": employee.psychotype,
            "psychotype_description": employee.psychotype_description,
        }
        
        return Response(psychotype_data, status=status.HTTP_200_OK)
    

class EmployeeFeedbackCountView(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        data = []
        for employee in employees:
            feedback_count = Feedback.objects.filter(employee=employee).count()
            data.append({
                'employee_id': employee.id,
                'created_at': employee.created_at,
                'psychotype': employee.psychotype,
                'psychotype_description': employee.psychotype_description,
                'feedback_count': feedback_count
            })
        return Response(data, status=status.HTTP_200_OK)


class FeedbackCreateView(APIView):
    def post(self, request):
        # Фильтруем пустые записи
        filtered_data = [
            feedback for feedback in request.data
            if feedback.get('ID_reviewer') not in [None, ''] and feedback.get('ID_under_review') not in [None, '']
        ]

        # Создаем сериализатор с отфильтрованными данными
        serializer = FeedbackSerializer(data=filtered_data, many=True)

        if serializer.is_valid():
            serializer.save()  # Сохраняем все объекты в БД с расчетом весов
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        feedbacks = Feedback.objects.all()
        serialized_feedbacks = [
            {
                "ID_reviewer": feedback.review_creator.id,
                "ID_under_review": feedback.employee.id,
                "review": feedback.text,
                "weight": feedback.weight,
                "is_self_review": feedback.is_self_review
            }
            for feedback in feedbacks
        ]
        return Response(serialized_feedbacks, status=status.HTTP_200_OK)


class FeedbackGenerateSummaryView(APIView):
    MAX_PROMPT_LENGTH = 20000  # Максимальная длина промта в символах

    def post(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Сотрудник не найден."}, status=status.HTTP_404_NOT_FOUND)

        reviews = Feedback.objects.filter(employee=employee).values("text", "weight")
        if not reviews:
            return Response({"detail": "Нет отзывов для данного сотрудника."}, status=status.HTTP_404_NOT_FOUND)

        prompts = self.prepare_prompts(reviews)
        all_summaries = []
        for prompt in prompts:
            evaluation = self.evaluate_reviews_with_llm(prompt)
            if isinstance(evaluation, dict) and "error" in evaluation:
                return Response({"detail": evaluation["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            summary_text = self.clean_summary_text(evaluation)
            all_summaries.append(summary_text)

        consolidated_summary = self.get_consolidated_summary(all_summaries)
        psychotype_data = self.analyze_psychotype(consolidated_summary)
        
        # Сохраняем сводку и психотип
        save_feedback_summary(employee_id, consolidated_summary, psychotype_data)

        return Response({
            "message": "Анализ завершен успешно.",
            "summary": consolidated_summary,
            "psychotype": psychotype_data
        }, status=status.HTTP_200_OK)

    def analyze_psychotype(self, consolidated_summary):
        prompt = (
            f"Вот общая сводка по сотруднику на основе отзывов:\n\n{consolidated_summary}\n\n"
            "На основе этой информации, определите психотип сотрудника. Верните краткий вывод о психотипе. "
            "Верни ответ в формате JSON без лишней информации и пояснения:\n"
            "{\n"
            '  "psychotype": "психотип сотрудника",\n'
            '  "psychotype_description": "Краткий вывод по психотипу сотрудника"\n'
            "}\n"
        )

        # Получаем ответ от LLM API
        evaluation = self.evaluate_reviews_with_llm(prompt)

        # Логируем ответ для отладки
        print("EVALUATION RESPONSE:", evaluation)

        # Проверка типа ответа
        if isinstance(evaluation, str):
            # Пробуем преобразовать строку в словарь
            try:
                evaluation_dict = json.loads(evaluation)
                # Проверяем нужные ключи в полученном ответе
                if "psychotype" in evaluation_dict and "psychotype_description" in evaluation_dict:
                    return evaluation_dict
                else:
                    print("Некорректная структура JSON.")
            except json.JSONDecodeError:
                print("Ошибка декодирования JSON:", evaluation)
        else:
            print("Ответ не является строкой.")

        # Значения по умолчанию, если JSON не найден или некорректен
        return {
            "psychotype": "Не определен",
            "psychotype_description": "Нет описания"
        }
        
    def prepare_prompts(self, reviews):
        aspects = Aspect.objects.values_list('text', flat=True)
        aspect_list = '\n'.join([f"{idx + 1}. {aspect}" for idx, aspect in enumerate(aspects)])
        base_prompt = (
            "Вот несколько отзывов(и их веса) о сотруднике:\n\n"
            "На основе этих отзывов и их весов, максимально объективно оцени сотрудника по шкале от 1 до 5 (оценка не обязательно должна быть целой)(учитывай веса отзывов. Ну тоесть чем меньше вес, тем меньше отзыв должен влиять на итоговую оценку аспекта. Если вес нулевой, то тогда этот отзыв вообще не должен учитываться) по следующим критериям:\n"
            f"{aspect_list}\n"
            "Добавьте краткое объяснение к каждому набранному баллу. Не ссылайся на какие-то конкретные отзывы в объяснениях. "
            "Также, основываясь на всей этой информации, сделай краткий вывод по сотруднику.\n"
            "Верните ответ в формате JSON, со следующей структурой(Аспект Профессионализм дан для примера, а так, анализ должен проихводиться по каждому аспекту который указан чуть выше):\n\n"
            "{\n"
            '  "Профессионализм": {"score": (определи общую оценку данного аспекта), "description": "Краткий вывод по этому аспекту"},\n'
            '  "Вывод": {"score": (определи общую оценку сотрудника), "description": "вывод по сотруднику"}\n'
            "}"
        )

        prompts = []
        current_prompt = base_prompt
        for i, review in enumerate(reviews, start=1):
            review_text = f"Отзыв {i} (вес: {review['weight']}):\n{review['text']}\n\n"
            if len(current_prompt) + len(review_text) > self.MAX_PROMPT_LENGTH:
                prompts.append(current_prompt)
                current_prompt = base_prompt  # Сбрасываем промт и добавляем базовый текст
            current_prompt += review_text

        if current_prompt:
            prompts.append(current_prompt)

        print(f"CURRENT PROMT: {current_prompt}")

        return prompts

    def get_consolidated_summary(self, all_summaries):
        # Формируем финальный запрос на основе промежуточных данных
        prompt = (
            "Вот сводки по нескольким аспектам сотрудника основе отзывов о нем:\n\n"
            + "\n\n".join(all_summaries) +
            "\n\nВ ответе должен содержаться итоговый ответ и оценка по каждому аспекту который есть во входящих данных. Верните ответ в формате JSON, со следующей структурой(Аспект Профессионализм дан для примера, а так, анализ должен проихводиться по каждому аспекту который содержится в сводках выше):\n\n"
            "{\n"
            '  "Профессионализм": {"score": (определи общую оценку данного аспекта), "description": "Краткий вывод по этому аспекту"},\n'
            '  "Вывод": {"score": (определи общую оценку сотрудника), "description": "Краткий вывод по сотруднику"}\n'
            "}"
        )

        evaluation = self.evaluate_reviews_with_llm(prompt)
        
        # Проверка на JSON-ответ
        if isinstance(evaluation, dict) and "text_response" in evaluation:
            # Пытаемся преобразовать текстовый ответ в JSON
            try:
                evaluation_json = json.loads(evaluation["text_response"])
                return evaluation_json
            except json.JSONDecodeError:
                raise Exception("Не удалось декодировать JSON из текстового ответа.")

        # Возвращаем JSON-ответ, если он корректно разобран
        return evaluation

    def evaluate_reviews_with_llm(self, prompt):
        prompt = prompt.replace("'", '"')  # Замена одинарных кавычек на двойные
        data = {
            "prompt": [prompt],
            "apply_chat_template": True,
            "system_prompt": "You are a helpful assistant.",
            "max_tokens": 2000,
            "n": 1,
            "temperature": 0.3
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                "https://vk-scoreworker-case.olymp.innopolis.university/generate",
                data=json.dumps(data), headers=headers
            )
            response.raise_for_status()

            # Попытка парсинга как JSON
            try:
                json_response = response.json()
                print("Ответ от LLM API (JSON):", json_response)
                return json_response  # Возвращаем JSON-ответ, если парсинг успешен
            except json.JSONDecodeError:
                # Обработка текстового ответа
                raw_text_response = response.text.strip()
                print("Ответ от LLM API (текст):", raw_text_response)
                return {"text_response": raw_text_response}  # Возвращаем текст в словаре

        except requests.exceptions.RequestException as e:
            print("Ошибка запроса к LLM:", str(e))
            return {"error": f"Ошибка запроса к LLM: {str(e)}"}

    def clean_summary_text(self, evaluation):
        # Если это текстовый ответ, возвращаем его сразу
        if "text_response" in evaluation:
            return evaluation["text_response"].strip()
        
        # Если это JSON-ответ, обрабатываем его как раньше
        clean_text = re.sub(r"^\*\*\d+\..*\n", "", json.dumps(evaluation, ensure_ascii=False), flags=re.MULTILINE)
        return clean_text.strip()
