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

if __name__ == "__main__":
    print(ModInverse(3, 11))
    print(ModInverse(10, 17))