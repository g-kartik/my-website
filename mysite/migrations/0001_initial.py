# Generated by Django 3.1.4 on 2020-12-16 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('session_id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
    ]
