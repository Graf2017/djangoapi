# Generated by Django 4.2 on 2023-05-09 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0003_alter_categories_options_alter_position_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='brand',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Brand'),
        ),
        migrations.AlterField(
            model_name='position',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='photos/%Y/%m/', verbose_name='Photo'),
        ),
    ]
