# Generated by Django 4.2.7 on 2024-05-14 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LabelModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='标签名称', max_length=255, unique=True)),
                ('type', models.CharField(choices=[('text', '文本'), ('audio', '音频'), ('video', '视频')], help_text='标签类型', max_length=10)),
                ('desc', models.CharField(help_text='标签描述', max_length=255)),
            ],
        ),
    ]