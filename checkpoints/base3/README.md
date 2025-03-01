base: version 3
finetune: version 1
dataset: tainovel.com, shannews.org medium {50000, 50000} https://huggingface.co/datasets/NorHsangPha/shan-novel-tainovel_com, https://huggingface.co/datasets/NorHsangPha/shan-news-shannews_org
MAX_ITERATIONS=200000
LEARNING_RATE=0.0001
NET_SPEC=[1,36,0,1 Ct3,3,32 Mp3,3 Lfys64 Lfx128 Lrx128 Lfx512 O1c###]