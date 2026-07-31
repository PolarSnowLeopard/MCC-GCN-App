import hashlib
import os
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from ml_models.models import MLModel

FIXTURE_DIR = Path(settings.BASE_DIR) / 'fixtures'

BUILTIN_MODELS = [
    {
        'name': 'MCC-GCN 4-Class Pretrain v2',
        'description': (
            '基于修复后的 CSD 数据处理与分子对隔离划分训练的四分类基础模型，'
            '适用于域内预测和后续微调。'
        ),
        'model_type': 'pretrained',
        'num_classes': 4,
        'is_builtin': True,
        'fixture_file': 'mcc_gcn_pretrained_v2.pth',
        'inference_config': {
            'schema_version': 1,
            'model_size': 'large',
            'feature_source': 'rdkit_smiles',
            'adjacency_type': 'OnlyCovalentBond',
            'pad_to': None,
            'checkpoint_sha256': (
                '197c7a2533b0e01c38a93c3f3137c87f4d6b2f2c4ead2e0edcf356fa050acc26'
            ),
        },
    },
    {
        'name': 'MCC-GCN 4-Class Finetune Exp+Minoxidil v1',
        'description': '在预训练基础上使用实验数据与 Minoxidil 数据微调的四分类模型。',
        'model_type': 'finetuned',
        'num_classes': 4,
        'is_builtin': True,
        'fixture_file': 'mcc_gcn_finetuned.pth',
        'inference_config': {
            'schema_version': 1,
            'model_size': 'large',
            'feature_source': 'rdkit_smiles',
            'adjacency_type': 'OnlyCovalentBond',
            'pad_to': 70,
            'checkpoint_sha256': (
                '7945aa2284aa305192eaace25a0fe94675b5e24f52c41df82e48e2d47e154e41'
            ),
        },
    },
]


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _install_fixture(source, destination, expected_sha256):
    actual_sha256 = _sha256(source)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f'Fixture checksum mismatch for {source.name}: '
            f'expected {expected_sha256}, got {actual_sha256}',
        )
    if destination.exists() and _sha256(destination) == actual_sha256:
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f'.{destination.name}.',
        dir=destination.parent,
    )
    os.close(fd)
    temporary_path = Path(temporary_name)
    try:
        shutil.copy2(source, temporary_path)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)
    return True


class Command(BaseCommand):
    help = '创建或更新内置模型（幂等操作）'

    def handle(self, *args, **options):
        dest_dir = Path(settings.MEDIA_ROOT) / 'models'
        dest_dir.mkdir(parents=True, exist_ok=True)

        for definition in BUILTIN_MODELS:
            meta = dict(definition)
            meta['inference_config'] = dict(meta['inference_config'])
            fixture_file = meta.pop('fixture_file')
            src = FIXTURE_DIR / fixture_file
            dest = dest_dir / fixture_file
            changed = _install_fixture(
                src,
                dest,
                meta['inference_config']['checkpoint_sha256'],
            )

            obj = MLModel.objects.filter(
                is_builtin=True,
                model_type=meta['model_type'],
            ).order_by('id').first()
            created = obj is None
            if created:
                obj = MLModel()
            for field, value in meta.items():
                setattr(obj, field, value)
            obj.model_file.name = f'models/{fixture_file}'
            obj.save()

            action = '已创建' if created else '已更新'
            fixture_status = '模型文件已替换' if changed else '模型文件未变化'
            self.stdout.write(
                self.style.SUCCESS(f'{action}: {obj}（{fixture_status}）'),
            )
