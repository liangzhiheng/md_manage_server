# Generated by Django 4.2.7 on 2024-05-06 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_manage', '0002_rename_description_labels_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videometa',
            name='type',
            field=models.TextField(choices=[('Film', '电影'), ('TvDrama', '电视剧'), ('Others', '其它')], help_text='视频类型'),
        ),
    ]