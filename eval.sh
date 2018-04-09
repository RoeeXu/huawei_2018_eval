# !/bin/bash
 
##############################################################
# 
# Copyright (c) 2018 USTC, Inc. All Rights Reserved
# 
##############################################################
# 
# File:    eval.sh
# Author:  roee
# Date:    2018/03/11 16:29:27
# Brief:
# 
# 
##############################################################

for eles in `ls`
do
{
    dir=$eles
    if [ -d $dir ]
    then
        python ecs.py $dir/train.txt $dir/input.txt $dir/output.txt > ecs_log
        python evaluate.py $dir
    fi
} &
done
wait

# vim: set expandtab ts=4 sw=4 sts=4 tw=100
