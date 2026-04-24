# AES Avalanche Effect ML Analysis

Analyzes the avalanche effect in AES encryption using machine learning. The avalanche effect is a critical security property where small changes in plaintext produce significant changes in ciphertext.

## Project Overview

This project studies how bit-flipping in plaintext affects ciphertext diffusion in AES-128 and applies ML models to understand the relationship.

## Components

- **aes.py** - Pure Python AES-128 implementation
- **aes_avalanche.py** - Dataset generation: single-bit flips in plaintext, measures ciphertext changes
- **aes_completeness.py** - Bit dependency analysis: tracks which output bits depend on each input bit
- **aes_round_analysis.py** - Round-by-round avalanche analysis with internal state tracking
- **aes_manual_verif.py** - Verification script: demonstrates avalanche effect with examples
- **ml_analysis.py** - ML models: Linear/Polynomial Regression and Random Forest on avalanche data

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Generate dataset:
```bash
python src/aes_avalanche.py
```

Analyze bit completeness:
```bash
python src/aes_completeness.py
```

Analyze round-by-round avalanche:
```bash
python src/aes_round_analysis.py
```

Verify avalanche effect:
```bash
python src/aes_manual_verif.py
```

Run ML analysis:
```bash
python src/ml_analysis.py
```

## Data

- **avalanche_dataset.csv** - Full avalanche dataset
- **avalanche_dataset_16bytes.csv** - Avalanche dataset for 16-byte payloads
- **avalanche_dataset_32bytes.csv** - Avalanche dataset for 32-byte payloads
- **avalanche_dataset_64bytes.csv** - Avalanche dataset for 64-byte payloads

## Results

- **completeness_matrix.npy** - 128×128 matrix of bit dependencies
- **full_dependency.npy** - Full dependency analysis
- **aes_completeness.png** - Completeness visualization
- **aes_round_avalanche.png** - Avalanche effect visualization

## Dependencies

- pandas: data handling
- scikit-learn: machine learning models
- numpy: numerical operations
- matplotlib: visualization