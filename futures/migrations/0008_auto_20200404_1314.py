# Generated by Django 3.0.4 on 2020-04-04 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0007_auto_20200403_2300'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='continuousfutures',
            options={'ordering': ('symbol',)},
        ),
        migrations.AlterModelOptions(
            name='exchange',
            options={'ordering': ('symbol',)},
        ),
    ]