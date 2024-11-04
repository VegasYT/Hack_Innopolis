# Generated by Django 5.1.2 on 2024-11-03 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0007_aspectsummary_weight'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aspectsummary',
            name='weight',
        ),
        migrations.AddField(
            model_name='feedback',
            name='weight',
            field=models.FloatField(default=0.0, verbose_name='Вес отзыва'),
        ),
    ]
