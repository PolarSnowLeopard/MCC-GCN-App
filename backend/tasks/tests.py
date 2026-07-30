
from django.test import SimpleTestCase

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
