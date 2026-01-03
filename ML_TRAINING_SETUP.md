# ML Training Pipeline Setup Guide

This guide explains how to set up and use the ML training pipeline for the IntelRouter system.

## Overview

The ML training pipeline:
- Trains Logistic Regression models on user feedback data (`ml_data` table)
- Stores models in Supabase Storage (not git)
- Evaluates on full dataset + last 30 days
- Only promotes models if no regression on recent data
- Runs automatically every 30 days via GitHub Actions

## Architecture

### Data Separation
- **`queries` table**: Inference logs and routing predictions (never used for training)
- **`ml_data` table**: Ground-truth labels from user feedback (only source for training)

### Training Flow
1. Training script loads ALL rows from `ml_data`
2. Extracts features using shared feature module
3. Trains Logistic Regression model
4. Evaluates on full test set + recent 30 days
5. Compares with active model
6. Uploads to Supabase Storage if better
7. Updates metadata table

### Inference Flow
1. Backend loads active model from Supabase Storage at startup
2. Extracts features using same feature module as training
3. Predicts difficulty + confidence
4. Returns "UNCERTAIN" if confidence < threshold
5. Stores prediction in `queries` table

## Setup Steps

### 1. Database Setup

Run the following SQL scripts in your Supabase SQL editor:

```sql
-- 1. Create model_metadata table (from model_metadata_setup.sql)
-- 2. Ensure ml_data table exists (from ml_data_setup.sql)
```

### 2. Supabase Storage Setup

1. Go to Supabase Dashboard → Storage
2. Create a new bucket named `ml-models`
3. Set it as **Private**
4. Add storage policy (run in SQL editor):

```sql
-- Allow service role full access to ml-models bucket
CREATE POLICY "Service role full access"
ON storage.objects FOR ALL
USING (bucket_id = 'ml-models')
WITH CHECK (bucket_id = 'ml-models');
```

### 3. Local Training Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download NLTK data:
```bash
python -c "import nltk; nltk.download('punkt_tab', quiet=True); nltk.download('averaged_perceptron_tagger_eng', quiet=True); nltk.download('wordnet', quiet=True)"
```

3. Run training locally:
```bash
python training/train.py
```

### 4. GitHub Actions Setup

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `SUPABASE_SERVICE_KEY`: Your Supabase service role key

3. The workflow will run automatically every 30 days
4. You can also trigger it manually: Actions → Train ML Model → Run workflow

## File Structure

```
app/
├── ml/
│   ├── features.py          # Shared feature extraction
│   ├── classifier.py         # Inference module (loads from Supabase)
│   ├── model_storage.py      # Supabase Storage utilities
│   └── model_metadata.py    # Model versioning
├── router/
│   └── hybrid_router.py     # Uses classifier for routing

training/
└── train.py                 # Training script

.github/workflows/
└── train_model.yml          # GitHub Actions cron job
```

## Training Configuration

Edit `training/train.py` to adjust:

- `CONFIDENCE_THRESHOLD = 0.6`: Minimum confidence for predictions
- `MIN_TRAINING_SAMPLES = 50`: Minimum samples required to train
- `TEST_SIZE = 0.2`: Test set size (20%)
- `RANDOM_STATE = 42`: Random seed for reproducibility

## Model Metadata

The `model_metadata` table tracks:
- `version`: Model version (e.g., "v20240101_120000")
- `accuracy`: Full test set accuracy
- `f1_score`: Full test set F1 score
- `confidence_threshold`: Confidence threshold used
- `training_timestamp`: When model was trained
- `is_active`: Whether this is the active model
- `metrics`: Full metrics JSON (includes recent data metrics)

## Monitoring

### Check Active Model
```python
from app.ml.model_metadata import get_active_model_metadata
metadata = get_active_model_metadata()
print(metadata)
```

### View All Models
Query the `model_metadata` table in Supabase:
```sql
SELECT version, accuracy, f1_score, is_active, training_timestamp 
FROM model_metadata 
ORDER BY created_at DESC;
```

### Training Logs
- Local: Check console output
- GitHub Actions: Check Actions tab in repository

## Troubleshooting

### "No active model found"
- Run training script to create first model
- Ensure `model_metadata` table exists
- Check Supabase Storage bucket exists

### "Failed to download model"
- Verify Supabase Storage bucket `ml-models` exists
- Check service key has storage access
- Verify model files exist in storage

### "Insufficient training data"
- Need at least 50 samples in `ml_data` table
- Collect more user feedback
- Use override feature to generate training data

### Training fails in GitHub Actions
- Check secrets are set correctly
- Verify Supabase credentials
- Check workflow logs for specific errors

## Best Practices

1. **Never train on `queries.final_label`** - Only use `ml_data`
2. **Monitor model performance** - Check metrics regularly
3. **Collect feedback** - More feedback = better models
4. **Review regressions** - If model doesn't promote, investigate
5. **Version control** - All models are versioned in metadata table

## Request → Response Flow

```
1. User submits query → POST /api/query
2. Backend extracts features (shared module)
3. Model predicts difficulty + confidence
4. If confidence < threshold → "UNCERTAIN"
5. Result stored in queries table (prediction only)
6. Response returned to user
7. Optional: User provides feedback → stored in ml_data
8. Optional: User uses override → automatically stored in ml_data
9. Every 30 days: Training script runs
   - Loads ALL ml_data rows
   - Trains new model
   - Evaluates on full + recent data
   - Compares with active model
   - Promotes if no regression
   - Uploads to Supabase Storage
```

## Next Steps

1. Run initial training to create first model
2. Monitor model performance
3. Collect user feedback
4. Let GitHub Actions handle periodic retraining

