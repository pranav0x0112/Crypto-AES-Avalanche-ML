# AES Avalanche Effect ML Analysis

Analyzes the avalanche effect in AES encryption using machine learning. The avalanche effect is a critical security property where small changes in plaintext produce significant changes in ciphertext.

## Project Overview

This project studies how bit-flipping in plaintext affects ciphertext diffusion in AES-128 and applies ML models to understand the relationship.

## Components

- **aes_avalanche.py** - Generates dataset: encrypts random plaintexts with single-bit flips, measures output changes (2000 samples)
- **aes_manual_verif.py** - Verification script: demonstrates avalanche effect with a concrete example
- **ml_analysis.py** - ML models: trains Linear Regression, Polynomial Regression, and Random Forest on avalanche data

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Generate dataset:
```bash
python src/aes_avalanche.py
```

Verify avalanche effect manually:
```bash
python src/aes_manual_verif.py
```

Analyze with ML models:
```bash
python src/ml_analysis.py
```

## Data

- **avalanche_dataset.csv** - Generated dataset with columns: `bit_flipped` (position), `avalanche` (proportion of bits changed)

## Dependencies

- pycryptodome: AES encryption
- pandas: data handling
- scikit-learn: machine learning models
- numpy: numerical operations
- matplotlib: visualization