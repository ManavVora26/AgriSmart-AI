# AgriSmart AI — Model Weights Directory

Place your trained model weights file here before running in "real" mode.

## Expected filename
```
disease_model.pt
```

## How to get the weights

**Option 1 — Member 3 will train the model:**
After training, Member 3 should:
1. Save weights: `torch.save({'model_state_dict': model.state_dict()}, 'disease_model.pt')`
2. Upload to a Google Drive or GitHub Release
3. Share the download link — add it to `backend/README.md`

**Option 2 — Quick download (placeholder for demo):**
A pre-trained EfficientNet-B0 on PlantVillage (~18 classes) can be downloaded from:
- [PlantVillage PyTorch Model (Kaggle)](https://www.kaggle.com/datasets/emmarex/plantdisease)

## Switching from mock to real mode

1. Place `disease_model.pt` in this directory
2. Edit `.env` file: `MODEL_MODE=real`
3. Restart the server: `uvicorn main:app --reload`

## Architecture expected

The model should be:
- **Architecture**: EfficientNet-B0 (from `timm`, `timm.create_model("efficientnet_b0", num_classes=18)`)
- **Input**: 224×224 RGB image, normalized with ImageNet mean/std
- **Output**: 18 logits (one per disease class)
- **Classes**: See `utils/label_map.py` for the full INDEX_TO_LABEL mapping
