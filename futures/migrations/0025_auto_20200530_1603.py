# Generated by Django 2.1 on 2020-05-30 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0024_auto_20200530_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rootsymbol',
            name='commission_type',
            field=models.IntegerField(choices=[(0, 'Percent'), (1, 'Fixed')], default=0),
        ),
    ]
