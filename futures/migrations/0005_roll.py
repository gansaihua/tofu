# Generated by Django 3.0.4 on 2020-04-03 22:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0004_auto_20200403_2039'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('roll_type', models.CharField(max_length=25)),
                ('ver', models.IntegerField()),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='futures.Code')),
                ('root_symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='futures.ContinuousFutures')),
            ],
        ),
    ]
