#!/bin/bash

# Define paths
MODEL_NAME="shn"
START_MODEL="mya"  # Using Myanmar model as a base
LANG_CODE="shn"
TESSTRAIN_REPO="$HOME/Labs/tesstrain"  # Adjust if tesstrain is in a different location
DATA_DIR="$TESSTRAIN_REPO/data"
TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata"
WORDLIST_FILE="$TESSTRAIN_REPO/data/shn.wordlist.txt"
NUMBERS_FILE="$TESSTRAIN_REPO/data/shn.numbers.txt"
PUNG_FILE="$TESSTRAIN_REPO/data/shn.punc.txt"

# Create the training directory
mkdir -p "$DATA_DIR/$MODEL_NAME"

# Generate training data from existing ground truth
cd $TESSTRAIN_REPO
make training MODEL_NAME=$MODEL_NAME START_MODEL=$START_MODEL LANG_CODE=$LANG_CODE TESSDATA=$TESSDATA_PREFIX WORDLIST_FILE=$WORDLIST_FILE NUMBERS_FILE=$NUMBERS_FILE PUNC_FILE=$PUNC_FILE

# Start LSTM fine-tuning
lstmtraining \
  --continue_from "$DATA_DIR/$START_MODEL.lstm" \
  --model_output "$DATA_DIR/$MODEL_NAME" \
  --traineddata "$DATA_DIR/$LANG_CODE/$LANG_CODE.traineddata" \
  --train_listfile "$DATA_DIR/$LANG_CODE.training_files.txt" \
  --max_iterations 5000

# Combine trained LSTM model into traineddata file
lstmtraining \
  --stop_training \
  --continue_from "$DATA_DIR/$MODEL_NAME_checkpoint" \
  --traineddata "$DATA_DIR/$LANG_CODE/$LANG_CODE.traineddata" \
  --model_output "$DATA_DIR/$MODEL_NAME.traineddata"

echo "Fine-tuning complete! Model saved at $DATA_DIR/$MODEL_NAME.traineddata"
