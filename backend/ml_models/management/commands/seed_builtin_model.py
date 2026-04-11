import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from ml_models.models import MLModel

FIXTURE_DIR = Path(settings.BASE_DIR) / 'fixtures'

BUILTIN_MODELS = [
    {
        'name': 'MCC-GCN Pretrained v1',
        'description': '基于 CSD 数据库预训练的通用基础模型，支持 4 分类共晶预测，适合作为微调基座。',
        'model_type': 'pretrained',
        'num_classes': 4,
        'is_builtin': True,
        'fixture_file': 'mcc_gcn_pretrained.pth',
    },
    {
        'name': 'MCC-GCN v1',
        'description': '在预训练基础上经过领域微调的最终模型，具备最佳预测性能，可直接用于共晶筛选。',
        'model_type': 'finetuned',
        'num_classes': 4,
        'is_builtin': True,
        'fixture_file': 'mcc_gcn_finetuned.pth',
    },
]


class Command(BaseCommand):
    help = '初始化内置模型（幂等操作）'

    def handle(self, *args, **options):
        dest_dir = Path(settings.MEDIA_ROOT) / 'models'
        dest_dir.mkdir(parents=True, exist_ok=True)

        for meta in BUILTIN_MODELS:
            fixture_file = meta.pop('fixture_file')
            if MLModel.objects.filter(is_builtin=True, name=meta['name']).exists():
                self.stdout.write(self.style.WARNING(f'已存在，跳过: {meta["name"]}'))
                continue

            src = FIXTURE_DIR / fixture_file
            dest = dest_dir / fixture_file
            shutil.copy2(src, dest)

            obj = MLModel(**meta)
            obj.model_file.name = f'models/{fixture_file}'
            obj.save()

            self.stdout.write(self.style.SUCCESS(f'已创建: {obj}'))
