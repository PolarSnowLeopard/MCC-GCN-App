import shutil
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from ml_models.models import MLModel

FIXTURE_PATH = Path(settings.BASE_DIR) / 'fixtures' / 'mcc_gcn_pretrained.pth'

MODEL_META = {
    'name': 'MCC-GCN Pretrained v1',
    'description': '基于多组分共晶图卷积网络（MCC-GCN）的预训练模型，支持 4 分类共晶预测。',
    'model_type': 'pretrained',
    'num_classes': 4,
    'is_builtin': True,
}


class Command(BaseCommand):
    help = '初始化内置预训练模型（幂等操作）'

    def handle(self, *args, **options):
        if MLModel.objects.filter(is_builtin=True, name=MODEL_META['name']).exists():
            self.stdout.write(self.style.WARNING('内置模型已存在，跳过'))
            return

        dest_dir = Path(settings.MEDIA_ROOT) / 'models'
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / 'mcc_gcn_pretrained.pth'
        shutil.copy2(FIXTURE_PATH, dest)

        obj = MLModel(**MODEL_META)
        obj.model_file.name = 'models/mcc_gcn_pretrained.pth'
        obj.save()

        self.stdout.write(self.style.SUCCESS(f'内置模型已创建: {obj}'))
