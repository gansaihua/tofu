# Generated by Django 2.1 on 2020-05-30 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0025_auto_20200530_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyBarChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.BigIntegerField()),
                ('open', models.FloatField(blank=True, null=True)),
                ('high', models.FloatField(blank=True, null=True)),
                ('low', models.FloatField(blank=True, null=True)),
                ('close', models.FloatField(blank=True, null=True)),
                ('volume', models.IntegerField(blank=True, null=True)),
                ('open_interest', models.IntegerField(blank=True, null=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='futures.Contract')),
            ],
            options={
                'db_table': 'futures_dailybar_changes',
            },
        ),
    ]