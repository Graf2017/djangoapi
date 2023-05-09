# Generated by Django 4.2 on 2023-05-04 08:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base_app', '0002_alter_client_basket'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categories',
            options={'ordering': ['name'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='position',
            options={'ordering': ['id'], 'verbose_name': 'Position', 'verbose_name_plural': 'Positions'},
        ),
        migrations.AddField(
            model_name='position',
            name='brand',
            field=models.CharField(max_length=40, null=True, verbose_name='Brand'),
        ),
        migrations.AlterField(
            model_name='position',
            name='categories',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pos', to='base_app.categories', verbose_name='Category of the position'),
        ),
        migrations.AlterField(
            model_name='position',
            name='photo',
            field=models.ImageField(blank=True, default=django.utils.timezone.now, upload_to='photos/%Y/%m/', verbose_name='Photo'),
            preserve_default=False,
        ),
    ]
