import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=150)),
                ('specialization', models.CharField(db_index=True, max_length=150)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('experience_years', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(80)])),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctors', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name', 'id'],
            },
        ),
    ]
