# Generated by Django 4.2.4 on 2023-10-10 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citas_app', '0003_rename_completarhsitorial_completarhistorial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='completarhistorial',
            name='completada',
        ),
        migrations.AddField(
            model_name='citamedica',
            name='completada',
            field=models.BooleanField(default=False),
        ),
    ]
