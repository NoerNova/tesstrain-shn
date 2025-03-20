base: version 3
finetune: version 15
datasets: large 300000
    shannews.org
    taifreedom.com
    shn.shanhumanrights.org
    tainovel.com
MAX_ITERATIONS=600000
LEARNING_RATE=0.00005
NET_SPEC=[1,0,0,1 Ct3,3,32 Mp3,3 Lfys64 Lfx128 Lrx128 Lfx512 O1c###]
FINETUNE_TYPE=Impact
PSM=6

best checkpoint candidated:
shn_0.036_15741_249800
image: 39%
pdf: 13%

shn_0.059_10787_120300
image: 2%
pdf: 33%

shn_0.064_10015_103100
image: 5%
pdf: 89%

shn_0.067_9186_85800
image: 5%
pdf: 89%