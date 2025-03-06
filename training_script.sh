#!/bin/bash

# Define paths
MODEL_NAME="shn"
LANG_CODE="shn"
TESSTRAIN_REPO="$HOME/Labs/tesstrain"
DATA_DIR="$TESSTRAIN_REPO/data"
TESSDATA_PREFIX="/usr/local/share/tessdata"
WORDLIST_FILE="$TESSTRAIN_REPO/data/shn.wordlist.txt"
NUMBERS_FILE="$TESSTRAIN_REPO/data/shn.numbers.txt"
PUNC_FILE="$TESSTRAIN_REPO/data/shn.punc.txt"
MAX_ITERATIONS=200000
LEARNING_RATE=0.0005

# Create the training directory
rm -rf "$DATA_DIR/$MODEL_NAME"
rm -r "$DATA_DIR/$MODEL_NAME.traineddata"
mkdir -p "$DATA_DIR/$MODEL_NAME"

# Generate training data
cd $TESSTRAIN_REPO
make training \
    MODEL_NAME=$MODEL_NAME \
    LANG_CODE=$LANG_CODE \
    TESSDATA=$TESSDATA_PREFIX \
    WORDLIST_FILE=$WORDLIST_FILE \
    PUNC_FILE=$PUNC_FILE \
    NET_SPEC="[1,36,0,1 Ct3,3,32 Mp3,3 Lfys64 Lfx128 Lrx128 Lfx512 O1c###]" \
    MAX_ITERATIONS=$MAX_ITERATIONS \
    LEARNING_RATE=$LEARNING_RATE
