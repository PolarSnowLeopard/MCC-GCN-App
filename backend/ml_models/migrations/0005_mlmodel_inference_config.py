from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ml_models', '0004_mlmodel_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlmodel',
            name='inference_config',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
