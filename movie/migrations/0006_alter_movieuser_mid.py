# Generated by Django 4.2.5 on 2024-11-06 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0005_customuser_groups_customuser_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movieuser',
            name='mid',
            field=models.IntegerField(),
        ),
    ]
