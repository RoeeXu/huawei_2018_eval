# !/usr/bin/env python
# -*- coding: utf-8 -*-
 
##############################################################
# 
# Copyright (c) 2018 USTC, Inc. All Rights Reserved
# 
##############################################################
# 
# File:    predicto.py
# Author:  roee
# Date:    2018/03/09 23:52:41
# Brief:
# 
# 
##############################################################

import time
import math


def time2stamp(t):
    timeArray = time.strptime(t, "%Y-%m-%d %H:%M:%S")
    stamp = int(time.mktime(timeArray))
    return stamp


def read_input(input_lines):
    args = {}
    Physical = input_lines[0].split()
    args['p_cpu'] = int(Physical[0])
    args['p_mem'] = int(Physical[1])
    args['p_hard'] = int(Physical[2])
    args['t_start'] = time2stamp(input_lines[-2:][0].strip())
    args['t_end'] = time2stamp(input_lines[-2:][1].strip())
    args['aim'] = input_lines[-4].strip()
    args['v_class'] = int(input_lines[2].strip())
    args['v_info'] = [line.strip().split() for line in input_lines[3:-5]]
    return args


def read_train(ecs_lines):
    flavor_info = {}
    for line in ecs_lines:
        eles = line.split()
        uuid = eles[0]
        flavorName = eles[1]
        createTime = time2stamp(eles[2] + ' ' + eles[3])
        if flavorName in flavor_info:
            flavor_info[flavorName].append([uuid, createTime])
        else:
            flavor_info[flavorName] = [[uuid, createTime]]
    return flavor_info


def compute_L(s, w, b):
    k = len(s) - 1
    wins = len(w)
    L = 0.0
    for i in range(wins, k+1):
        l = 0.0
        for j in range(wins):
            l += (w[j] * s[i-1-j])
        l += b
        l -= s[i]
        L += (l * l)
    return L


def compute_dw(s, w, b):
    dw = []
    k = len(s) - 1
    wins = len(w)
    for x in range(wins):
        L = 0.0
        for i in range(wins, k+1):
            l = 0.0
            for j in range(wins):
                l += (w[j] * s[i-1-j])
            l += b
            l -= s[i]
            L += (2 * l * s[i-1-x])
        dw.append(L)
    return dw


def compute_db(s, w, b):
    k = len(s) - 1
    wins = len(w)
    L = 0.0
    for i in range(wins, k+1):
        l = 0.0
        for j in range(wins):
            l += (w[j] * s[i-1-j])
        l += b
        l -= s[i]
        L += (2 * l)
    return L

def pred_tru(train, args):
    t_max = 0
    t_min = 1e11
    for f in train:
        for _, stamp in train[f]:
            t_max = stamp if stamp > t_max else t_max
            t_min = stamp if stamp < t_min else t_min
    pred1 = {}
    for f, _, _ in args['v_info']:
        pr = float(len(train.get(f, []))) * (args['t_end'] - args['t_start']) / (t_max - t_min)
        if pr - int(pr) >= 0.5:
            pred1[f] = int(pr) + 1
        else:
            pred1[f] = int(pr)
    return pred1             


def print_pred(pred):
    res = []
    num = 0
    for f in pred:
        num += pred[f]
        res.append(' '.join(map(str, [f, pred[f]])))
    return [str(num)] + res


def place_compute(pred, args):
    ''' 
        From $pred and $args we can know:
            +-------+-------+-------+-------+
            |fname  |cpu    |mem    |num    |
            +-------+-------+-------+-------+
            |f_1    |a_1    |b_1    |c_1    |
            |f_2    |a_2    |b_2    |c_2    |
            |...    |...    |...    |...    |
            |f_n    |a_n    |b_n    |c_n    |
            +-------+-------+-------+-------+
        I assume I will use $m physical servers,
        then I can list table:
            +-------+-------+-------+-------+-------+
            |phy_no |f_1    |f_2    |...    |f_n    |
            +-------+-------+-------+-------+-------+
            |1      |x_11   |x_12   |...    |x_1n   |
            |2      |x_21   |x_22   |...    |x_2n   |
            |...    |...    |...    |...    |...    |
            |m      |x_m1   |x_m2   |...    |x_mn   |
            +-------+-------+-------+-------+-------+
        This problem have some restrictions:
            +=====================================================+
            |1. Sum_{j=1..n}(a_j * x_ij) <= args['p_cpu']   i=1..m|
            |2. Sum_{j=1..n}(b_j * x_ij) <= args['p_mem']   i=1..m|
            |3. Sum_{i=1..m}(x_ij)       == c_j             j=1..n|
            |4. x_ij is natural number                            |
            +=====================================================+
        If there exists a set of {x_ij}, then the result is permitted.
        I should minimize the variable $m.
    '''
    f = []
    for fname, cpu, mem in args['v_info']:
        f.append([fname, int(cpu), int(mem), pred[fname]])
    flag = 1 if args['aim'] == 'CPU' else 2
    for i in range(len(f)-1):
        for j in range(i+1, len(f)):
            if f[i][flag] < f[j][flag]:
                temp = f[i]
                f[i] = f[j]
                f[j] = temp
    for i in range(len(f)-1):
        for j in range(i+1, len(f)):
            if f[i][flag] == f[j][flag] and f[i][3-flag] < f[j][3-flag]:
                temp = f[i]
                f[i] = f[j]
                f[j] = temp
    p_cpu = args['p_cpu']
    p_mem = args['p_mem']
    place = []
    pos = 0
    while len(f) != 0:
        fname, cpu, mem, num = f[0]
        if num == 0:
            del f[0]
            continue
        mem /= 1000.0
        if pos == len(place):
            n_cpu = 0
            n_mem = 0.0
            res = {}
            place.append([n_cpu, n_mem, res])
            continue
        else:
            n_cpu = place[pos][0]
            n_mem = place[pos][1]
            res = place[pos][2]
        if n_cpu + cpu <= p_cpu and n_mem + mem <= p_mem:
            if fname in res:
                place[pos][2][fname] += 1
            else:
                place[pos][2][fname] = 1
            f[0][3] -= 1
            place[pos][0] += cpu
            place[pos][1] += mem
            pos = 0
        else:
            pos += 1
    rrrr = [str(len(place))]
    for i, p in enumerate(place):
        l = [i+1]
        dic = p[2]
        for fname in dic:
            l += [fname, dic[fname]]
        rrrr += [' '.join(map(str, l))]
    return rrrr


def predict_vm(ecs_lines, input_lines):
    result = []
    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result
    train = read_train(ecs_lines)
    args = read_input(input_lines)
    pred = pred_tru(train, args)
    result += print_pred(pred)
    result += ['']
    result += place_compute(pred, args)
    return result


# vim: set expandtab ts=4 sw=4 sts=4 tw=100
