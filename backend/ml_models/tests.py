
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from .inference import resolve_inference_config
from .models import MLModel


class InferenceConfigTests(TestCase):
    def test_explicit_config_overrides_legacy_builtin_padding(self):
        model = MLModel.objects.create(
            name='Pretrained v2',
            model_type='pretrained',
            model_file='models/pretrained.pth',
            is_builtin=True,
            inference_config={
                'schema_version': 1,
                'model_size': 'large',
                'feature_source': 'rdkit_smiles',
                'adjacency_type': 'OnlyCovalentBond',
                'pad_to': None,
            },
        )

        self.assertIsNone(resolve_inference_config(model)['pad_to'])

    def test_empty_config_retains_legacy_builtin_fallback(self):
        model = MLModel.objects.create(
            name='Legacy fine-tuned',
            model_type='finetuned',
            model_file='models/finetuned.pth',
            is_builtin=True,
        )

        self.assertEqual(resolve_inference_config(model)['pad_to'], 70)


class SeedBuiltinModelTests(TestCase):
    def test_existing_builtin_record_and_fixture_are_updated(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            fixture_dir = root / 'fixtures'
            media_root = root / 'media'
            fixture_dir.mkdir()
            source = fixture_dir / 'candidate.pth'
            source.write_bytes(b'validated checkpoint')
            expected_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
            definition = {
                'name': 'MCC-GCN Pretrained v2',
                'description': 'corrected',
                'model_type': 'pretrained',
                'num_classes': 4,
                'is_builtin': True,
                'fixture_file': source.name,
                'inference_config': {
                    'schema_version': 1,
                    'model_size': 'large',
                    'feature_source': 'rdkit_smiles',
                    'adjacency_type': 'OnlyCovalentBond',
                    'pad_to': None,
                    'checkpoint_sha256': expected_sha256,
                },
            }
            existing = MLModel.objects.create(
                name='MCC-GCN Pretrained v1',
                model_type='pretrained',
                model_file='models/old.pth',
                is_builtin=True,
            )

            command_module = (
                'ml_models.management.commands.seed_builtin_model'
            )
            with (
                override_settings(MEDIA_ROOT=media_root),
                patch(f'{command_module}.FIXTURE_DIR', fixture_dir),
                patch(f'{command_module}.BUILTIN_MODELS', [definition]),
            ):
                call_command('seed_builtin_model')

            existing.refresh_from_db()
            self.assertEqual(existing.name, 'MCC-GCN Pretrained v2')
            self.assertEqual(
                existing.model_file.name,
                'models/candidate.pth',
            )
            self.assertIsNone(existing.inference_config['pad_to'])
            self.assertEqual(
                (media_root / 'models' / 'candidate.pth').read_bytes(),
                source.read_bytes(),
            )
