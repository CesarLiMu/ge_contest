#!/bin/bash

CONDA=/home/rwoodard/local/miniconda3
P0RN=/home/rwoodard/cgit/user/rwoodard/p0rn
#OUTFILE=/tmp/cron_daily_snipe_hunt.out
OUTFILE=$P0RN/cron_daily_snipe_hunt.out
OUTFILE_TMP=${OUTFILE}.txt
#OUTFILE_TMP2=${OUTFILE}.tmp2

# From ~/.zshrc_local
export PYTHONPATH=$HOME/local/lib/python2.7/site-packages:$PYTHONPATH

# From ~/.zshrc_work
export PYTHONPATH=$HOME/cgit/user/rwoodard:$PYTHONPATH
export PYTHONPATH=$HOME/cgit/app/fraud/python:$PYTHONPATH
export PYTHONPATH=$HOME/cgit/app/inv-quality:$PYTHONPATH
export PYTHONPATH=$HOME/cgit/resources:$PYTHONPATH
export PYTHONPATH=$HOME/rw:$PYTHONPATH
export PYTHONPATH=$HOME/local/lib/python2.7/site-packages:$PYTHONPATH

cd $P0RN

echo '----------------' > $OUTFILE_TMP
echo 'START snipe_hunt' >> $OUTFILE_TMP
echo `date` >> $OUTFILE_TMP
echo '' >> $OUTFILE_TMP
echo '' >> $OUTFILE_TMP
echo 'A bit hacky but...hey!' >> $OUTFILE_TMP
echo '' >> $OUTFILE_TMP
echo '' >> $OUTFILE_TMP

source $CONDA/bin/activate py27
$CONDA/envs/py27/bin/python $P0RN/snipe_hunt.py --query both --force >> $OUTFILE_TMP
source $CONDA/envs/py27/bin/deactivate

echo `date` >> $OUTFILE_TMP
echo 'END snipe_hunt' >> $OUTFILE_TMP
echo '--------------' >> $OUTFILE_TMP

cat $OUTFILE_TMP >> $OUTFILE

#mailx -s "The Porning Report" dhimrod@appnexus.com < $OUTFILE_TMP
$CONDA/envs/py27/bin/python $P0RN/send_porn_email.py $OUTFILE_TMP


