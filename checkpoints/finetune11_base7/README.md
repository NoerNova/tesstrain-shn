base: finetune 7 version 3
finetune: version 11
dataset: shannews.org large 180000 https://huggingface.co/datasets/NorHsangPha/shan-news-shannews_org
MAX_ITERATIONS=200000
LEARNING_RATE=0.0001
NET_SPEC=[1,0,0,1 Ct3,3,32 Mp3,3 Lfys64 Lfx128 Lrx128 Lfx512 O1c###]

BCER train=0.027%,
BWER train=0.396%
BEST_FOR=pdf