# Generated by Django 3.0.5 on 2020-04-26 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0014_contract_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='rootsymbol',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
