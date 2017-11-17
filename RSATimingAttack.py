import math
import sys
from multiprocessing import Process, Queue

def ModInverse(a, n):
    (t, t_new, r, r_new) = (0, 1, int(n), int(a))

    while r_new:
        quotient = r//r_new
        (t, t_new) = (t_new, t - quotient*t_new)
        (r, r_new) = (r_new, r - quotient*r_new)

    if r > 1:
        raise ArithmeticError("ERROR: %d is not invertible modulo %d. \n r was: %d, new_r was %d " % (a, n, r, r_new))
    else:
        if t < 0:
            t += n
        
    return t

def MontgomeryProduct (a, b, n, nPrime, r):
    t = a * b
    m = t * nPrime % r
    u = (t + m*n)/r

    if u >= n:
        return (u-n, True)
    else:
        return (u, False)

def rsa(a, d, n, nPrime, r):
    aBar = (a*r)%n
    xBar = (1*r)%n
    k = len(d)
    sub_count = 0
    for i in range(0, k):
        sub = False
        xBar, tmp = MontgomeryProduct(xBar, xBar, n, nPrime, r)
        if d[i] == '1':
            xBar, sub = MontgomeryProduct(aBar, xBar, n, nPrime, r)
        sub_count += int(sub)
    x, tmp = MontgomeryProduct(xBar, 1, n, nPrime, r)
    return x, sub_count 

def rsa_guess(a, d, n, nPrime, r, bit):
    aBar = (a*r)%n
    xBar = (1*r)%n
    d_approx = d[:bit]
    d_approx += '1'
    k = len(d_approx)
    sub = False
    for i in range(0, k):
        xBar, tmp = MontgomeryProduct(xBar, xBar, n, nPrime, r)
        if d_approx[i] == '1':
            xBar, sub = MontgomeryProduct(aBar, xBar, n, nPrime, r)
    x, tmp = MontgomeryProduct(xBar, 1, n, nPrime, r)
    return x, sub

def do_guess(q_t, q_f, messageList, d, n, nPrime, r, bit):
    m_true = []
    m_false = []
    for message in messageList:
        tmp, sub = rsa_guess(message[0], d, n, nPrime, r, bit)
        if sub:
            m_true.append(message)
        else:
            m_false.append(message)
    q_t.put(m_true)
    q_f.put(m_false)

def split_messages(data, d, n, nPrime, r, bit):
    messageList = data
    q_t = Queue()
    q_f = Queue()
    processes = []
    numOfProcs = 8
    chunkSize = len(messageList)//numOfProcs
    index = 0
    NP = 0
    while index < len(messageList):
        p = Process(target=do_guess, args=(q_t, q_f, messageList[index:index+chunkSize], d, n, nPrime, r, bit))
        NP += 1
        p.start()
        index += chunkSize
        processes.append(p)

    m_true = []
    m_false = []
    for i in range(NP):
        m_true += q_t.get()
        m_false += q_f.get()

    while processes:
        processes.pop().join()    
    return (m_true, m_false)

def n_Prime(n):
    k = math.floor(math.log(int(n), 2)) + 1
    r = int(math.pow(2,k))
    rInverse = ModInverse(r,n)
    nPrime = (r * rInverse - 1)//n 
    return (r, nPrime)

def RSATimingAttack(n, data, delta):
    (r, n_prime) = n_Prime(n)
    guessed = False
    key_approx = '1'
    bit = 1
    while not guessed:
        (m_true, m_false) = split_messages(data, key_approx, n, n_prime, r, bit)
        with open("%04d"%bit+'.dat', 'w') as f_approx:
            f_approx.write("Message, Signature, Duration, Step\n")
            for m in m_true:
                f_approx.write("%s,1\n" % ','.join(map(str,m)))
            for m in m_false:
                f_approx.write("%s,2\n" % ','.join(map(str,m)))
            f_approx.close()
        
        avg = lambda items: float(sum(items)) / len(items)
        tavg = map(avg, zip(*m_true))[2]
        favg = map(avg, zip(*m_false))[2]

        print "Ratio: \t",tavg/favg, "\tDifference:", abs(tavg-favg)

        if abs(tavg - favg) > delta:
            key_approx += '1' #Bit Guessed as 1
            print "Guessing next bit is 1."
        else:
            key_approx += '0' #Bit Guessed as 1
            print "Guessing next bit is 0."
        
        print "Derived key: ", key_approx

        testMessage1, c = rsa(data[0][0], key_approx, n, n_prime, r)
        testMessage2, c = rsa(data[1][0], key_approx, n, n_prime, r)

        if (testMessage1 == data[0][1] and testMessage2 == data[1][1]):
            print "Guessed Correctly! Private key is: \t", key_approx
            guessed = True
        bit += 1

if __name__ == "__main__":
    path = sys.argv[1]
    delta = sys.argv[2]
    data = []
    with open(path+'/data.csv', 'rb') as f_data:
        _ = f_data.readline()
        n,e = f_data.readline().split(',')
        n = int(n)
        e = int(e)
        _ = f_data.readline()

        data = [[int(x) for x in line.split(',')] for line in f_data]
    
    RSATimingAttack(n, data, int(delta))