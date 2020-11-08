# Generated by Django 3.1.2 on 2020-11-08 23:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='IncomingInteractionLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship', models.CharField(max_length=140)),
                ('origin_instance', models.CharField(max_length=140)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship_str', models.CharField(max_length=140)),
                ('item', models.ManyToManyField(to='data_upload_app.Item')),
            ],
        ),
        migrations.CreateModel(
            name='RankingCluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ranking_feature', models.CharField(blank=True, max_length=140, null=True)),
                ('number_of_instances', models.PositiveIntegerField(blank=True, null=True)),
                ('instances_ranking', models.CharField(blank=True, max_length=140, null=True)),
                ('links_ranking', models.CharField(blank=True, max_length=140, null=True)),
                ('master_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_upload_app.item')),
            ],
        ),
        migrations.CreateModel(
            name='Measure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140)),
                ('measure_type', models.CharField(max_length=140)),
                ('unit_of_measurement', models.CharField(max_length=140)),
                ('statistic_type', models.CharField(max_length=140)),
                ('measurement_reference_time', models.CharField(max_length=140)),
                ('measurement_precision', models.CharField(max_length=140)),
                ('value_dtype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_upload_app.datatype')),
            ],
        ),
        migrations.CreateModel(
            name='InstanceLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('landing_instance', models.CharField(max_length=140)),
                ('relationship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_upload_app.relationship')),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.JSONField()),
                ('measure', models.JSONField()),
                ('abm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_upload_app.abstractmodel')),
                ('iil', models.ManyToManyField(to='data_upload_app.IncomingInteractionLink')),
                ('link', models.ManyToManyField(to='data_upload_app.InstanceLink')),
            ],
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140, unique=True)),
                ('dtype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_upload_app.datatype')),
            ],
        ),
        migrations.CreateModel(
            name='AMLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instances_value_dtype', models.CharField(max_length=140)),
                ('time_link', models.BooleanField()),
                ('link_criteria', models.CharField(max_length=140)),
                ('values', models.CharField(max_length=140)),
                ('relationship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_upload_app.relationship')),
            ],
        ),
        migrations.AddField(
            model_name='abstractmodel',
            name='attribute',
            field=models.ManyToManyField(to='data_upload_app.Attribute'),
        ),
        migrations.AddField(
            model_name='abstractmodel',
            name='link',
            field=models.ManyToManyField(to='data_upload_app.AMLink'),
        ),
        migrations.AddField(
            model_name='abstractmodel',
            name='master_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_upload_app.item'),
        ),
        migrations.AddField(
            model_name='abstractmodel',
            name='measure',
            field=models.ManyToManyField(to='data_upload_app.Measure'),
        ),
    ]