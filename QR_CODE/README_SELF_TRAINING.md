# AI Smart QR Shield — Self-Training Random Forest

## What changed

This version does **not** distribute a pre-trained Random Forest model.

The project now creates and trains its own `RandomForestClassifier` using:

- `data/qr_dataset.csv`
- 23 extracted security features
- 80/20 stratified train/test split
- 300 decision trees
- balanced class weights

### Training behavior

1. If `model/qr_model.pkl` does not exist, the first prediction automatically runs `model/train_model.py`.
2. The model is trained from the project's dataset.
3. The newly trained model is saved locally for subsequent predictions.
4. From the **ML Model Architecture** page, use **Train / Retrain Random Forest Now** to create a fresh model whenever required.

The distributed ZIP intentionally contains **no `qr_model.pkl` or `feature_names.pkl`**.

## Run

Open a terminal inside the `QR_CODE` folder:

```bash
python prepare_dataset.py
python model/train_model.py
streamlit run app.py
```

You can also simply run the Streamlit app. If no model exists, the first QR prediction will train it automatically.

## Verify training

```bash
python test_prediction.py
```

The training script prints:

- Training accuracy
- Test accuracy
- Classification report
- Confusion matrix

It also creates:

- `model/qr_model.pkl`
- `model/feature_names.pkl`
- `model/training_metrics.json`

These generated files are local training outputs and are not included in the distributed ZIP.

## Important academic point

This is a **project-owned, locally trained Random Forest model**, not a pre-trained third-party AI model. Scikit-learn provides the Random Forest algorithm implementation; the model parameters are learned from this project's dataset during training.
