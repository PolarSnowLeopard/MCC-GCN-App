from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ml_models', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mlmodel',
            name='is_large',
        ),
        migrations.AddField(
            model_name='mlmodel',
            name='is_builtin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='mlmodel',
            name='user',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='models',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
