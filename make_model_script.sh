#!/bin/bash

CHECKPOINT="shn_0.034_17056_285400"

lstmtraining --stop_training --continue_from data/shn/checkpoints/$CHECKPOINT.checkpoint --traineddata data/shn/shn.traineddata --model_output data/shn.traineddata
sudo cp data/shn.traineddata /usr/local/share/tessdata/
ocrmypdf -l shn --force-ocr data/demo/testpdf.pdf data/demo/testpdf_out_15.pdf