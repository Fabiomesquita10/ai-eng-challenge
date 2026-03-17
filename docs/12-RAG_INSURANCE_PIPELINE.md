# 🧠 RAG Pipeline: Insurance Specialist — Hybrid + RRF + Rerank

Based on benchmarks and production practices (2024–2025), the best-performing approach is a **three-stage hybrid pipeline**. This document explains each step in detail.

---

## Overview

```
Query → [1. Hybrid Search] → ~120–150 candidates
     → [2. RRF] → Single ranked list
     → [3. Rerank] → Top 5–10 chunks for LLM
```

---

## Passo 1 — Hybrid Search (gerar candidatos)

Executas duas buscas **em paralelo** com a mesma query:

### Busca vetorial (dense)

- A query é convertida em embedding e comparada com os embeddings dos chunks.
- O vector DB devolve os **top-100** mais similares.
- **Funciona bem para:** paráfrases, sinónimos, perguntas em linguagem natural.
- **Falha quando:** a query tem tokens exatos (IDs, códigos de erro como ORA-00942, nomes técnicos como HNSW).

### Busca BM25 (lexical)

- Conta a frequência das palavras da query nos documentos.
- Pondera termos raros (IDF) e a frequência no doc (TF).
- **Funciona bem para:** exact match, IDs, códigos, negações ("não suportado").
- **Falha quando:** a query usa sinónimos ou linguagem diferente do documento.

### Resultado

- Duas listas (ex: 100 da dense + 100 da BM25).
- Com fusão, ficas com **~120–150 candidatos únicos**.
- Cobres ambos os casos — semântico e lexical.

---

## Passo 2 — RRF (Reciprocal Rank Fusion)

As duas listas têm scores em escalas diferentes (similaridade vetorial vs score BM25). Em vez de comparar números diretamente, usas RRF para combinar pelos **ranks**:

1. Cada documento recebe um score: `1/(k + posição)` em cada lista.
   - Ex: k=60, documento na posição 1 → 1/61
   - Na posição 10 → 1/70

2. Os scores das duas listas são **somados**.
   - Um doc que aparece no top-5 de ambas fica com score alto.
   - Um que só aparece numa lista fica mais baixo.

3. Ordenas por score total e deduplicas os candidatos.

### Resultado

- Uma única lista ordenada, sem precisar de normalizar scores.
- Simples e robusto.

---

## Passo 3 — Reranking com cross-encoder

Tens ~120 candidatos, mas o LLM só precisa de **5–10**. Um cross-encoder avalia cada par (query, chunk) com um único forward pass — mais preciso que o bi-encoder usado na busca inicial:

1. **Input:** `[query] [SEP] [chunk]` concatenados.
2. **Output:** score de relevância (0–1).
3. Ordenas por score e ficas com os **top-5 ou top-10**.

### Resultado

- Chunks de alta precisão para o LLM.
- Eliminas falsos positivos que passaram por BM25 ou dense.

---

## Summary

| Stage | Input | Output |
|-------|-------|--------|
| 1. Hybrid | Query | ~120–150 candidates (dense + BM25) |
| 2. RRF | Two ranked lists | Single ranked list |
| 3. Rerank | Query + candidates | Top 5–10 chunks |

---

*Back to [Documentation Index](./README.md) | [06 - Model & RAG](./06-MODEL_TRAINING_AND_RAG.md)*
