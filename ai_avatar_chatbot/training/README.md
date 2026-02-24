# Training notebooks

This directory contains Jupyter notebooks for training and fine-tuning models.

## ASR Training (`asr_training.ipynb`)

Fine-tune Whisper on custom dataset for better accuracy in specific domains.

## TTS Training (`tts_training.ipynb`)

Train XTTS model with custom voice for personalized speech synthesis.

## Dataset Structure

```
datasets/
├── asr/
│   ├── train_audio/
│   ├── train_transcriptions.txt
│   ├── eval_audio/
│   └── eval_transcriptions.txt
├── tts/
│   ├── speaker_voice/
│   └── speaker_metadata.json
└── knowledge_base/
    └── documents/
```

## Usage

1. Prepare your dataset in the structure above
2. Open corresponding notebook
3. Configure training parameters
4. Run cells to train
5. Export trained model
