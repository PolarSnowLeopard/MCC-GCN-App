
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from ml_models.models import MLModel
from .serializers import BatchPredictionCreateSerializer


class BatchPredictionCreateSerializerTests(SimpleTestCase):
    def test_accepts_valid_molecule_pairs(self):
        serializer = BatchPredictionCreateSerializer(data={
            'model_id': 1,
            'pairs': [
                {
                    'api_smiles': 'CCO',
                    'coformer_smiles': 'O=C(O)c1ccccc1O',
                },
                {
                    'api_smiles': 'Nc1ccnc(N)[n+]1[O-]',
                    'coformer_smiles': 'O=C(O)CCC(=O)O',
                },
            ],
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(len(serializer.validated_data['pairs']), 2)

    def test_reports_the_invalid_row_and_field(self):
        serializer = BatchPredictionCreateSerializer(data={
            'model_id': 1,
            'pairs': [
                {
                    'api_smiles': 'CCOC(=O)c1ccnc(c1)C(=O)OCC',
                    'coformer_smiles': 'O=C(O)CCC(=O)O',
                },
                {
                    'api_smiles': 'CCOC(=O)c1ccnc(c2)C(=O)OCC',
                    'coformer_smiles': 'O=C(O)CCC(=O)O',
                },
            ],
        })

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['pairs'][0], {})
        self.assertEqual(
            str(serializer.errors['pairs'][1]['api_smiles'][0]),
            'Invalid SMILES.',
        )

    def test_rejects_an_empty_batch(self):
        serializer = BatchPredictionCreateSerializer(data={
            'model_id': 1,
            'pairs': [],
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('pairs', serializer.errors)


class PredictionInferenceConfigTests(TestCase):
    def test_single_prediction_uses_model_specific_no_padding_config(self):
        user = get_user_model().objects.create_user(
            username='tester',
            password='secret',
        )
        model = MLModel.objects.create(
            name='Pretrained v2',
            model_type='pretrained',
            model_file='models/pretrained-v2.pth',
            is_builtin=True,
            inference_config={
                'schema_version': 1,
                'model_size': 'large',
                'feature_source': 'rdkit_smiles',
                'adjacency_type': 'OnlyCovalentBond',
                'pad_to': None,
            },
        )
        client = APIClient()
        client.force_authenticate(user=user)
        result = {
            'prediction': 1,
            'label': 'Salt',
            'probabilities': [0.1, 0.7, 0.1, 0.1],
            'api_smiles': 'CCO',
            'coformer_smiles': 'O',
        }

        with patch('tasks.views.run_predict', return_value=result) as predict:
            response = client.post(
                '/api/tasks/predict/',
                {
                    'model_id': model.id,
                    'api_smiles': 'CCO',
                    'coformer_smiles': 'O',
                },
                format='json',
            )

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(predict.call_args.kwargs['pad_to'])
        self.assertEqual(
            predict.call_args.kwargs['model_size'],
            'large',
        )
