# Generated by Django 2.2.6 on 2021-11-16 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20211116_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Выберите группу', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
    ]
