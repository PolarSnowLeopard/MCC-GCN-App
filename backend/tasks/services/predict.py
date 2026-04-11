import logging
import threading

import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.data import Data

from mcc_gcn.models.gcn import GCNNet
from mcc_gcn.featurize.rdkit_coformer import RDKitCoformer
from mcc_gcn.featurize.cocrystal import Cocrystal

logger = logging.getLogger(__name__)

CLASS_LABELS = {0: 'Negative', 1: 'Salt', 2: 'Cocrystal', 3: 'Hydrate/Solvate'}

_model_cache = {}
_cache_lock = threading.Lock()


def _load_model(model_path, num_classes=4):
    with _cache_lock:
        if model_path in _model_cache:
            return _model_cache[model_path]
        device = torch.device('cpu')
        model = GCNNet(num_classes=num_classes).to(device)
        state = torch.load(model_path, map_location=device, weights_only=True)
        model.load_state_dict(state)
        model.eval()
        _model_cache[model_path] = model
        logger.info("Loaded model %s (classes=%d)", model_path, num_classes)
        return model


def _build_pyg_data(smiles1, smiles2):
    c1 = RDKitCoformer(smiles1, input_type='smiles')
    c2 = RDKitCoformer(smiles2, input_type='smiles')
    cc = Cocrystal(c1, c2)
    V = cc.VertexMatrix.feature_matrix()
    A = cc.CCGraphTensor(t_type='OnlyCovalentBond', hbond=False, pipi_stack=False, contact=False)

    x = torch.tensor(V, dtype=torch.float32)
    A_t = torch.tensor(A, dtype=torch.float32)
    edge_index = torch.nonzero(A_t.sum(1), as_tuple=False).t()
    return Data(x=x, edge_index=edge_index)


def predict_single(api_smiles, coformer_smiles, model_path=None, num_classes=4):
    model = _load_model(model_path, num_classes)
    data = _build_pyg_data(api_smiles, coformer_smiles)

    with torch.no_grad():
        batch = torch.zeros(data.x.size(0), dtype=torch.long)
        output = model(data.x, data.edge_index, batch)
        probs = F.softmax(output, dim=1).cpu().numpy()[0]

    pred = int(np.argmax(probs))
    return {
        'prediction': pred,
        'label': CLASS_LABELS[pred],
        'probabilities': [round(float(p), 4) for p in probs],
        'api_smiles': api_smiles,
        'coformer_smiles': coformer_smiles,
    }


def predict_batch(pairs, model_path=None, num_classes=4):
    results = []
    for p in pairs:
        try:
            r = predict_single(p['api_smiles'], p['coformer_smiles'], model_path, num_classes)
        except Exception as e:
            r = {
                'api_smiles': p['api_smiles'],
                'coformer_smiles': p['coformer_smiles'],
                'error': str(e),
            }
        results.append(r)
    return results
