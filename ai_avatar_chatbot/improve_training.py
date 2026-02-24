#!/usr/bin/env python
"""
Training improvement script for AI Avatar Chatbot
Helps diagnose and fix training issues
"""
import os
import sys
from pathlib import Path
import subprocess

def check_training_setup():
    """Check and setup training environment"""

    print("🔧 AI Avatar Chatbot - Training Setup Checker")
    print("=" * 55)
    print()

    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required for training")
        return False
    else:
        print("✅ Python version OK")

    # Check training directory
    training_dir = Path(__file__).parent / "training"
    if training_dir.exists():
        print("✅ Training directory exists")
    else:
        print("❌ Training directory missing")
        return False

    # Check datasets directory
    datasets_dir = training_dir / "datasets"
    if datasets_dir.exists():
        print("✅ Datasets directory exists")
    else:
        print("⚠️  Datasets directory missing - creating...")
        datasets_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Datasets directory created")

    # Check for required packages
    required_packages = [
        "torch",
        "transformers",
        "datasets",
        "accelerate",
        "peft",
        "bitsandbytes",
        "scipy",
        "soundfile",
        "librosa"
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        install = input("Install missing packages? (y/n): ").lower().strip()
        if install == 'y':
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"✅ Installed {package}")
                except subprocess.CalledProcessError:
                    print(f"❌ Failed to install {package}")
        else:
            print("Skipping package installation")

    # Check for training notebooks
    notebook_files = ["asr_training.ipynb", "tts_training.ipynb"]
    for notebook in notebook_files:
        notebook_path = training_dir / notebook
        if notebook_path.exists():
            print(f"✅ {notebook} found")
        else:
            print(f"❌ {notebook} missing")

    print("\n📚 Training Setup Complete!")
    print("\nTo start training:")
    print("1. Prepare your dataset in training/datasets/")
    print("2. Open training/asr_training.ipynb for speech recognition")
    print("3. Open training/tts_training.ipynb for voice synthesis")
    print("4. Follow the notebook instructions")

    return True

def create_sample_dataset():
    """Create sample dataset structure"""

    print("\n📁 Creating sample dataset structure...")

    base_dir = Path(__file__).parent / "training" / "datasets"

    # ASR dataset structure
    asr_dir = base_dir / "asr"
    asr_train_audio = asr_dir / "train_audio"
    asr_eval_audio = asr_dir / "eval_audio"

    # TTS dataset structure
    tts_dir = base_dir / "tts"
    tts_voice_dir = tts_dir / "speaker_voice"

    # Knowledge base
    kb_dir = base_dir / "knowledge_base" / "documents"

    directories = [
        asr_train_audio, asr_eval_audio, tts_voice_dir, kb_dir
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory.relative_to(base_dir.parent.parent)}")

    # Create sample files
    sample_transcript = asr_dir / "train_transcriptions.txt"
    if not sample_transcript.exists():
        with open(sample_transcript, 'w') as f:
            f.write("# Sample transcription file\n")
            f.write("# Format: audio_file.wav|transcription text\n")
            f.write("sample1.wav|Hello, this is a sample transcription\n")
        print(f"✅ Created sample {sample_transcript.name}")

    sample_metadata = tts_dir / "speaker_metadata.json"
    if not sample_metadata.exists():
        import json
        metadata = {
            "speaker_name": "Sample Speaker",
            "language": "en",
            "sample_rate": 22050,
            "description": "Sample speaker for TTS training"
        }
        with open(sample_metadata, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Created sample {sample_metadata.name}")

    print("\n📝 Next steps:")
    print("1. Add your audio files to the respective directories")
    print("2. Update transcription files with actual text")
    print("3. Run the training notebooks")

if __name__ == "__main__":
    success = check_training_setup()

    if success:
        create_sample = input("\nCreate sample dataset structure? (y/n): ").lower().strip()
        if create_sample == 'y':
            create_sample_dataset()

    print("\n🎯 Training setup check complete!")
    print("For more help, check the training/README.md file")