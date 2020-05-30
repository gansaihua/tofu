# Generated by Django 3.0.5 on 2020-05-28 23:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('futures', '0020_auto_20200504_0708'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContinuousFutures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('version', models.IntegerField()),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='futures.Contract')),
                ('root_symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='futures.RootSymbol')),
            ],
            options={
                'ordering': ('datetime',),
                'get_latest_by': 'datetime',
            },
        ),
    ]