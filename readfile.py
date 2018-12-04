import numpy as np
import sys
import os

with open('record.txt') as f:
    for each_line in f :
        read = each_line.split(",")
    # print(each_line)
    print(read)