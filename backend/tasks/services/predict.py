import random
import hashlib

CLASS_LABELS = {0: '无共晶', 1: '共晶 I 型', 2: '共晶 II 型', 3: '共晶 III 型'}


def predict_single(api_smiles, coformer_smiles, model_path=None):
    """MVP mock: deterministic based on input hash so same inputs give same results"""
    seed = int(hashlib.md5(f"{api_smiles}:{coformer_smiles}".encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    probs = [rng.random() for _ in range(4)]
    total = sum(probs)
    probs = [round(p / total, 4) for p in probs]
    pred = probs.index(max(probs))
    return {
        'prediction': pred,
        'label': CLASS_LABELS[pred],
        'probabilities': probs,
        'api_smiles': api_smiles,
        'coformer_smiles': coformer_smiles,
    }


def predict_batch(pairs, model_path=None):
    return [predict_single(p['api_smiles'], p['coformer_smiles'], model_path) for p in pairs]
