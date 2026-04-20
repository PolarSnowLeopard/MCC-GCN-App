from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('ml_models', '0003_remove_is_large_add_is_builtin'),
    ]
    operations = [
        migrations.AddField(
            model_name='mlmodel',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='published', max_length=20),
        ),
    ]
