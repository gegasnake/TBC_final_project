# Generated by Django 5.1.4 on 2024-12-15 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='events_created',
            field=models.IntegerField(default=0),
        ),
    ]