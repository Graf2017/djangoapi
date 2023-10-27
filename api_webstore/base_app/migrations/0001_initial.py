# Generated by Django 4.2 on 2023-10-25 18:18

import base_app.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL, verbose_name='Carts')),
            ],
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Categories name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slugs URL')),
                ('image', models.ImageField(blank=True, upload_to=base_app.models.categories_image_upload_path, verbose_name='Image')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='First name')),
                ('last_name', models.CharField(max_length=50, verbose_name='Last name')),
                ('phone', models.CharField(max_length=15, verbose_name='Phone number')),
                ('city', models.CharField(max_length=50, verbose_name='City')),
                ('address', models.CharField(max_length=100, verbose_name='Address')),
                ('index', models.CharField(blank=True, max_length=10, null=True, verbose_name='Index')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery', to=settings.AUTH_USER_MODEL, verbose_name='Delivery')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='Date create')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='Last update')),
                ('order_status', models.CharField(choices=[('New', 'New'), ('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Finished', 'Finished'), ('Canceled', 'Canceled')], default='Pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('Cash on delivery', 'Cash on delivery'), ('Online payment', 'Online payment')], max_length=20, null=True)),
                ('delivery', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delivery', to='base_app.delivery', verbose_name='Delivery')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Order')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='URL')),
                ('brand', models.CharField(blank=True, max_length=40, null=True, verbose_name='Brand')),
                ('description', models.CharField(max_length=500, verbose_name='Describe')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='Date create')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='Date update')),
                ('is_published', models.BooleanField(default=True, verbose_name='Is published')),
                ('in_stock', models.BooleanField(default=True, verbose_name='In stock')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('categories', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Category', to='base_app.categories', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Position',
                'verbose_name_plural': 'Positions',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField()),
                ('saved_title', models.CharField(blank=True, max_length=150)),
                ('saved_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('saved_total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_item', to='base_app.order')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='base_app.position')),
            ],
        ),
        migrations.CreateModel(
            name='OnlinePayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_url', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Canceled', 'Canceled'), ('Refunded', 'Refunded'), ('Finished', 'Finished')], default='Pending', max_length=20)),
                ('order', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='online_payment', to='base_app.order')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to=base_app.models.image_upload_path, verbose_name='Image')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='base_app.position', verbose_name='Position')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=0)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_item', to='base_app.cart')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='base_app.position')),
            ],
        ),
    ]
