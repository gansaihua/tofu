# Generated by Django 2.1 on 2020-04-27 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0017_auto_20200427_1342'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='minutebar',
            name='date_added',
        ),
        migrations.RemoveField(
            model_name='minutebar',
            name='date_updated',
        ),
        migrations.RemoveField(
            model_name='minutebarchange',
            name='datetime_temp',
        ),
        migrations.AlterField(
            model_name='minutebarchange',
            name='datetime',
            field=models.BigIntegerField(),
        ),
    ]