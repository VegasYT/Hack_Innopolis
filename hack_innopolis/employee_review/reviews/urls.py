from django.urls import path
from .views import *



urlpatterns = [
    path('api/feedback', FeedbackCreateView.as_view(), name='feedback-create'),
    path('api/feedback/generate-summary/<int:employee_id>', FeedbackGenerateSummaryView.as_view(), name='generate-summary'),

    # path('api/aspects/', AspectListView.as_view(), name='aspect-list'),

    path('api/aspects', AspectView.as_view(), name='aspect-list-create'),  # Для создания и получения всех аспектов
    path('api/aspects/<int:pk>', AspectDetailView.as_view(), name='aspect-detail'),  # Для получения, обновления и удаления аспекта
    path('api/feedback/<int:employee_id>', FeedbackByEmployeeView.as_view(), name='feedback-by-employee'),  # Получение отзывов для сотрудника
    path('api/aspect-summaries/<int:employee_id>', AspectSummaryByEmployeeView.as_view(), name='aspect-summary-by-employee'), # Получение всех AspectSummary по employee_id
    path('api/general-summaries/<int:employee_id>', GeneralSummaryByEmployeeView.as_view(), name='general-summary-by-employee'), # Для получения всех Generalsumm пользователя
    path('api/employee/<int:employee_id>/psychotype', EmployeePsychotypeView.as_view(), name='employee-psychotype'), # Информация о психотипе сотрудника
    path('api/employees/feedback-count', EmployeeFeedbackCountView.as_view(), name='employee-feedback-count'), # Получение всех сотрудников, их психотипы и количество отзывов о них
]