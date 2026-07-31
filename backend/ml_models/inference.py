DEFAULT_INFERENCE_CONFIG = {
    'schema_version': 1,
    'model_size': 'large',
    'feature_source': 'rdkit_smiles',
    'adjacency_type': 'OnlyCovalentBond',
    'pad_to': None,
}

LEGACY_BUILTIN_PAD_TO = {
    'pretrained': 178,
    'finetuned': 70,
}


def resolve_inference_config(model):
    config = dict(DEFAULT_INFERENCE_CONFIG)
    if model.inference_config:
        config.update(model.inference_config)
    elif model.is_builtin:
        config['pad_to'] = LEGACY_BUILTIN_PAD_TO.get(model.model_type)

    if config['schema_version'] != 1:
        raise ValueError(
            f'Unsupported inference config schema: {config["schema_version"]}',
        )
    if config['model_size'] not in {'small', 'large'}:
        raise ValueError(f'Unsupported model size: {config["model_size"]}')
    if config['feature_source'] != 'rdkit_smiles':
        raise ValueError(
            f'Unsupported feature source: {config["feature_source"]}',
        )
    if config['adjacency_type'] != 'OnlyCovalentBond':
        raise ValueError(
            f'Unsupported adjacency type: {config["adjacency_type"]}',
        )

    pad_to = config['pad_to']
    if pad_to is not None and (not isinstance(pad_to, int) or pad_to < 1):
        raise ValueError(f'Invalid pad_to value: {pad_to!r}')
    return config
