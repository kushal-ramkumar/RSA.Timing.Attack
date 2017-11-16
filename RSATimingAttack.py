import math

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

def nPrime(n):
    k = math.floor(math.log(int(n), 2)) + 1
    r = int(math.pow(2,k))
    rInverse = ModInverse(r,n)
    nPrime = (r * rInverse - 1)//n 
    return (r, nPrime)

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

if __name__ == "__main__":
    message = 10113892728
    print "Message : " + str(message)
    #d = '111111010000101111101001101011111'
    d = "{0:b}".format(8490832735)
    n = int(10967535067)
    #e = '11111'
    e = "{0:b}".format(31)
    r, nPrime = nPrime(n)
    encMessage, tmp = rsa(message, str(e), n, nPrime, r)
    decMessage, tmp = rsa(encMessage, str(d), n, nPrime, r)
    if decMessage == message:
        print "Decryption Successful " + str(decMessage)
    else:
        print "Decryption Failed!"