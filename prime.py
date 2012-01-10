#!/usr/bin/env python
#
# Calcula un determinado numero de numeros primos
# Despachando procesos por core.
# 
#
import sys
import time
import math
from multiprocessing import Process, Pool, cpu_count

#Check if the user give the number of processes to dispatch
if len(sys.argv) >= 2:
    process_to_disppatch = int(sys.argv[1])
    if not process_to_disppatch:
        process_to_disppatch = cpu_count()
else:
    process_to_disppatch = 1

print "Process to dispatch: %d"%process_to_disppatch

def is_prime(number):
    fnumber = float(number)
    prime = True
    root = math.sqrt(number)
    if root % 1:
        prime = False
    else:
        maxi = math.ceil(root)
        i = 2
        while i <=  maxi:
            if not number % i:
                prime = False
                break
            i += 1 
    #print prime, number
    return prime, number

po = Pool(process_to_disppatch)
c = time.time()
results  = po.map(is_prime, (k for k in xrange(3,1000000)))
print "Processing time was: ", time.time() - c

# remove if you want to see the prime numbers :-)
sys.exit()
print len(results)
results.sort(None, lambda x: x[1])

for prime, number in results:
    if prime:
        print number, prime

