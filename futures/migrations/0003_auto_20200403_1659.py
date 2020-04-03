# Generated by Django 2.1 on 2020-04-03 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0002_auto_20200403_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='code',
            name='exchange',
        ),
        migrations.AddField(
            model_name='continuousfutures',
            name='exchange',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='futures.Exchange'),
        ),
    ]
