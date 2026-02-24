# Models

Pre-trained model placeholders and paths.

## Structure

```
models/
├── asr/
│   └── whisper-small/    # Whisper model (auto-downloaded on first use)
├── tts/
│   └── xtts/             # XTTS v2 model (auto-downloaded on first use)
└── wav2lip/
    ├── checkpoints/      # Wav2Lip checkpoint
    └── face_detection/   # Face detection model
```

## Downloading Models

Models are automatically downloaded on first use, but you can pre-download them:

### ASR Models
```bash
python -c "import whisper; whisper.load_model('base')"
```

### TTS Models
```bash
python -m TTS.cli --text "Hello" --model_name "tts_models/en/ljspeech/xtts_v2"
```

### Wav2Lip (Optional)
```bash
# Download from https://github.com/justinlin610/Wav2Lip
# Place checkpoint in models/wav2lip/checkpoints/
```

## Model Sizes

### Whisper
- tiny: ~39M (fastest, lowest accuracy)
- base: ~140M (recommended for speed/accuracy)
- small: ~244M
- medium: ~769M
- large: ~1.5B (slowest, highest accuracy)

### Storage Requirements
- ASR: 500MB - 3GB
- TTS: 500MB - 1GB
- Wav2Lip: 200MB

## GPU Support

For faster inference, install PyTorch with CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Model Optimization

For production deployment:
1. Quantize models (int8/fp16)
2. Export to ONNX format
3. Use TensorRT for NVIDIA GPUs
4. Use CoreML for Apple devices
