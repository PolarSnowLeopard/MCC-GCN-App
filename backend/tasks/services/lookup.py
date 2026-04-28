"""Resolve a chemical name or CAS number to a SMILES string.

Calling external chemistry databases directly from the browser is unreliable
because of:

* CORS — most upstream services don't return permissive CORS headers, so
  same-origin policy blocks the response in browsers.
* Geographical access — PubChem and several NIH services intermittently
  block IPs originating from outside the US (especially shared / data-center
  ranges), which is exactly what most of our deployments look like.
* Upstream API churn — PubChem renamed its property fields in 2025
  (``CanonicalSMILES`` → ``SMILES``), silently breaking older clients.

We therefore proxy SMILES resolution through the backend and try several
upstream sources in turn, returning the first hit. All HTTP errors are
swallowed locally; the caller only sees ``None`` on a complete miss.
"""
from __future__ import annotations

import logging
import re

import requests

logger = logging.getLogger(__name__)

_TIMEOUT = 6  # seconds, per upstream
_USER_AGENT = 'MCC-GCN/1.0 (+https://github.com/PolarSnowLeopard/MCC-GCN-App)'
_HEADERS = {'User-Agent': _USER_AGENT, 'Accept': 'application/json,text/plain,*/*'}

_CAS_RE = re.compile(r'^\d{2,7}-\d{2}-\d$')


def _is_cas(query: str) -> bool:
    return bool(_CAS_RE.match(query))


def _try_pubchem(query: str) -> str | None:
    """PubChem PUG REST. Tries the new field name first, then the legacy one."""
    base = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name'
    for prop in ('SMILES', 'CanonicalSMILES'):
        url = f'{base}/{requests.utils.quote(query)}/property/{prop}/JSON'
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        except requests.RequestException as exc:
            logger.info('pubchem %s lookup failed for %r: %s', prop, query, exc)
            continue
        if resp.status_code != 200:
            continue
        try:
            payload = resp.json()
        except ValueError:
            continue
        props = payload.get('PropertyTable', {}).get('Properties') or []
        if not props:
            continue
        smiles = props[0].get(prop) or props[0].get('SMILES') or props[0].get('CanonicalSMILES')
        if smiles:
            return smiles
    return None


def _try_cactus(query: str) -> str | None:
    """NIH NCI Chemical Identifier Resolver — accepts names *and* CAS numbers."""
    url = f'https://cactus.nci.nih.gov/chemical/structure/{requests.utils.quote(query)}/smiles'
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
    except requests.RequestException as exc:
        logger.info('cactus lookup failed for %r: %s', query, exc)
        return None
    if resp.status_code != 200:
        return None
    smiles = resp.text.strip().splitlines()[0].strip() if resp.text else ''
    # Cactus returns "Page not found (404)" body with status 404, but also
    # sometimes plain HTML on success — keep only what looks like a SMILES.
    if smiles and not smiles.lower().startswith('<') and ' ' not in smiles:
        return smiles
    return None


def _try_opsin(query: str) -> str | None:
    """OPSIN — IUPAC name parser hosted by University of Cambridge."""
    if _is_cas(query):
        return None  # OPSIN only handles names
    url = f'https://opsin.ch.cam.ac.uk/opsin/{requests.utils.quote(query)}.smi'
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
    except requests.RequestException as exc:
        logger.info('opsin lookup failed for %r: %s', query, exc)
        return None
    if resp.status_code != 200:
        return None
    smiles = resp.text.strip()
    if smiles and not smiles.lower().startswith('<'):
        return smiles
    return None


_SOURCES = (
    ('pubchem', _try_pubchem),
    ('cactus', _try_cactus),
    ('opsin', _try_opsin),
)


def resolve_smiles(query: str) -> tuple[str | None, str | None]:
    """Return ``(smiles, source_name)`` for the first upstream that resolves.

    Returns ``(None, None)`` if every upstream fails or the query is empty.
    """
    query = (query or '').strip()
    if not query:
        return None, None

    for name, fn in _SOURCES:
        try:
            hit = fn(query)
        except Exception:  # noqa: BLE001 — never let one bad upstream kill the rest
            logger.exception('unexpected error from %s for %r', name, query)
            continue
        if hit:
            return hit, name
    return None, None
