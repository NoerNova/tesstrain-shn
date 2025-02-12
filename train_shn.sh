#!/bin/bash

# Define paths
MODEL_NAME="shn"
LANG_CODE="shn"
TESSTRAIN_REPO="$HOME/Labs/tesstrain"  # Adjust if needed
DATA_DIR="$TESSTRAIN_REPO/data"
TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata"
WORDLIST_FILE="$TESSTRAIN_REPO/data/shn.wordlist.txt"
NUMBERS_FILE="$TESSTRAIN_REPO/data/shn.numbers.txt"
PUNC_FILE="$TESSTRAIN_REPO/data/shn.punc.txt"

# Create the training directory
mkdir -p "$DATA_DIR/$MODEL_NAME"

# Generate training data
cd $TESSTRAIN_REPO
make training MODEL_NAME=$MODEL_NAME LANG_CODE=$LANG_CODE TESSDATA=$TESSDATA_PREFIX WORDLIST_FILE=$WORDLIST_FILE NUMBERS_FILE=$NUMBERS_FILE PUNC_FILE=$PUNC_FILE

# Start training from scratch
lstmtraining \
  --model_output "$DATA_DIR/$MODEL_NAME" \
  --traineddata "$DATA_DIR/$LANG_CODE/$LANG_CODE.traineddata" \
  --train_listfile "$DATA_DIR/$LANG_CODE.training_files.txt" \
  --max_iterations 100

# Convert final model to traineddata format
lstmtraining \
  --stop_training \
  --continue_from "$DATA_DIR/$MODEL_NAME_checkpoint" \
  --traineddata "$DATA_DIR/$LANG_CODE/$LANG_CODE.traineddata" \
  --model_output "$DATA_DIR/$MODEL_NAME.traineddata"

echo "Training complete! Model saved at $DATA_DIR/$MODEL_NAME.traineddata"
