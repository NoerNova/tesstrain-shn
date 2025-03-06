base: version 3
finetune: version 9
dataset: shannews.org medium 10000 https://huggingface.co/datasets/NorHsangPha/shan-news-shannews_org
MAX_ITERATIONS=30000
LEARNING_RATE=0.0001
NET_SPEC=[1,36,0,1 Ct3,3,32 Mp3,3 Lfys64 Lfx128 Lrx128 Lfx512 O1c###]

BCER train=0.217%, 
BWER train=1.074%
BEST_FOR=pdf