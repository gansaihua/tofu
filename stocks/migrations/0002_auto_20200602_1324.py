# Generated by Django 3.0.6 on 2020-06-02 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='daybar',
            name='amount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='daybar_changes',
            name='amount',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
