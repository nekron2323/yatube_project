# Generated by Django 2.2.6 on 2021-11-13 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20211112_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Семантический указатель группы'),
        ),
    ]
