#!/bin/bash

CHEKCPOINT_DIR="checkpoints/best"
CHECKPOINT="shn_0.034_17056_285400"
TESSDIR="/opt/homebrew/share/tessdata"

lstmtraining --stop_training --continue_from $CHEKCPOINT_DIR/$CHECKPOINT.checkpoint --traineddata $CHEKCPOINT_DIR/shn.traineddata --model_output data/shn.traineddata
sudo cp data/shn.traineddata $TESSDIR/
# ocrmypdf -l shn --force-ocr data/demo/testpdf.pdf data/demo/testpdf_out_15.pdf
