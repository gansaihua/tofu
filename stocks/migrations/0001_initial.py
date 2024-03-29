# Generated by Django 2.1 on 2020-06-02 19:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('futures', '0027_auto_20200530_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=30)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('asset', models.IntegerField(choices=[
                 (0, 'Stock'), (1, 'Stock Index'), (2, 'Bond Index')], default=0)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('exchange', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='futures.Exchange')),
            ],
        ),
        migrations.CreateModel(
            name='DayBar',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('open', models.FloatField(blank=True, null=True)),
                ('high', models.FloatField(blank=True, null=True)),
                ('low', models.FloatField(blank=True, null=True)),
                ('close', models.FloatField(blank=True, null=True)),
                ('volume', models.IntegerField(blank=True, null=True)),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           to='stocks.Code', unique_for_date='datetime')),
            ],
            options={
                'get_latest_by': 'datetime',
            },
        ),
        migrations.CreateModel(
            name='DayBar_Changes',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.BigIntegerField()),
                ('open', models.FloatField(blank=True, null=True)),
                ('high', models.FloatField(blank=True, null=True)),
                ('low', models.FloatField(blank=True, null=True)),
                ('close', models.FloatField(blank=True, null=True)),
                ('volume', models.IntegerField(blank=True, null=True)),
                ('code', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='stocks.Code')),
            ],
        ),
        migrations.AddIndex(
            model_name='daybar',
            index=models.Index(fields=['datetime'], name='daybar_dt_idx2'),
        ),
    ]
