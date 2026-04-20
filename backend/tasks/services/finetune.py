import csv
import logging

import numpy as np
import torch
import torch.nn as nn
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader

from mcc_gcn.models.gcn import GCNNet, train_epoch, evaluate
from mcc_gcn.models.metrics import calculate_metrics
from mcc_gcn.featurize.rdkit_coformer import RDKitCoformer
from mcc_gcn.featurize.cocrystal import Cocrystal

logger = logging.getLogger(__name__)


def _build_labeled_data(api_smiles, coformer_smiles, label):
    c1 = RDKitCoformer(api_smiles, input_type='smiles')
    c2 = RDKitCoformer(coformer_smiles, input_type='smiles')
    cc = Cocrystal(c1, c2)
    V = cc.VertexMatrix.feature_matrix()
    A = cc.CCGraphTensor(t_type='OnlyCovalentBond', hbond=False, pipi_stack=False, contact=False)
    x = torch.tensor(V, dtype=torch.float32)
    A_t = torch.tensor(A, dtype=torch.float32)
    edge_index = torch.nonzero(A_t.sum(1), as_tuple=False).t()
    return Data(x=x, edge_index=edge_index, y=torch.tensor(label, dtype=torch.long))


def parse_training_csv(csv_path):
    """Parse CSV with columns: api_smiles, coformer_smiles, label"""
    dataset = []
    errors = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                api_smi = row['api_smiles'].strip()
                cf_smi = row['coformer_smiles'].strip()
                label = int(row['label'])
                data = _build_labeled_data(api_smi, cf_smi, label)
                dataset.append(data)
            except Exception as e:
                errors.append(f"Row {i+2}: {e}")
                logger.warning("Skipping row %d: %s", i+2, e)
    return dataset, errors


def run_finetune(base_model_path, csv_path, output_path, config, progress_callback=None):
    """
    Run fine-tuning and return training metrics.

    Args:
        base_model_path: Path to pretrained model weights
        csv_path: Path to training CSV
        output_path: Path to save fine-tuned model
        config: dict with epochs, batch_size, learning_rate, train_layers, weight_decay, num_classes
        progress_callback: optional callable(epoch, total_epochs, metrics_dict)

    Returns:
        dict with training results (best_val_acc, epochs_trained, etc.)
    """
    device = torch.device('cpu')
    num_classes = config.get('num_classes', 4)
    epochs = config.get('epochs', 50)
    batch_size = config.get('batch_size', 16)
    lr = config.get('learning_rate', 3e-4)
    weight_decay = config.get('weight_decay', 0.3)
    train_layers = config.get('train_layers', 3)

    dataset, parse_errors = parse_training_csv(csv_path)
    if len(dataset) < 2:
        raise ValueError(f"Need at least 2 valid training samples. Got {len(dataset)}. Errors: {parse_errors}")

    np.random.seed(42)
    indices = np.random.permutation(len(dataset))
    split = max(2, int(len(dataset) * 0.8))
    train_data = [dataset[i] for i in indices[:split]]
    val_data = [dataset[i] for i in indices[split:]] if split < len(dataset) else train_data

    # drop_last avoids BatchNorm error when last batch has only 1 sample
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True,
                              drop_last=(len(train_data) > batch_size))
    val_loader = DataLoader(val_data, batch_size=256, shuffle=False)

    model = GCNNet(num_classes=num_classes).to(device)
    model.load_state_dict(torch.load(base_model_path, map_location=device, weights_only=True))
    model.ft_setting(train_dense_layer=train_layers)

    class_weights = torch.FloatTensor([1, 1, 1, 2]).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=lr, weight_decay=weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=3, min_lr=1e-5,
    )

    best_val_acc = 0.0
    log_lines = []

    for epoch in range(1, epochs + 1):
        train_labels, train_preds, train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
        val_labels, val_preds, val_loss = evaluate(model, val_loader, criterion, device)
        scheduler.step(val_loss)

        _, train_bacc, train_acc = calculate_metrics(train_labels, train_preds, num_classes)
        _, val_bacc, val_acc = calculate_metrics(val_labels, val_preds, num_classes)

        line = f"Epoch {epoch}/{epochs} | train_loss={train_loss:.4f} train_acc={train_acc:.4f} | val_loss={val_loss:.4f} val_acc={val_acc:.4f} val_bacc={val_bacc:.4f}"
        log_lines.append(line)

        if val_bacc > best_val_acc:
            best_val_acc = val_bacc
            torch.save(model.state_dict(), output_path)

        if progress_callback:
            progress_callback(epoch, epochs, {
                'train_loss': train_loss, 'train_acc': train_acc,
                'val_loss': val_loss, 'val_acc': val_acc, 'val_bacc': val_bacc,
            })

    if best_val_acc == 0.0:
        torch.save(model.state_dict(), output_path)

    return {
        'best_val_bacc': round(best_val_acc, 4),
        'total_epochs': epochs,
        'train_samples': len(train_data),
        'val_samples': len(val_data),
        'parse_errors': parse_errors[:10],
        'log': '\n'.join(log_lines),
    }
