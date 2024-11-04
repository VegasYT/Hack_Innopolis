# Панель для HR [VK ScoreWorker]

## 📋 Описание проекта
**HR-Панель** — это система, которая на основе отзывов о сотруднике генерирует по нему краткую сводку, определяет психотип сотрудника и присваивает числовые оценки, показывающие мнение коллег об этом работнике

### ⚙️ Установка
Шаг 1: Установка Python версии 3.11.

Шаг 2: Установка библиотек:
```bash
   pip install -r hack_innopolis/requirements.txt
```
Шаг 3: Установка nodeJS(Ver. 20.15.0) и npm(Ver. 10.07.0):
```bash
   Установите нужные инструменты по инструкции с официального сайта
```
Шаг 4: Установка зависимостей node_modules:
```bash
   cd hack_innopolis/front
   npm install
```

### ✔️ Запуск
Шаг 1: Запуск бэкенда:
```bash
   python hack_innopolis/employee_review/manage.py runserver
```
Шаг 2: Запуск фронтенда:
```bash
   cd hack_innopolis/front
   npm run dev
```
Архитектура БД
![BD](https://i.imgur.com/lIelXS0.png)
