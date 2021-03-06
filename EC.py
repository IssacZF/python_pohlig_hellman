######################################################################
# Matt Watson
# Directed Reading Program Project
# Elliptic Curve Implementation
######################################################################

import DRP

# Class for representing an elliptic curve
class Elliptic_Curve:
    def __init__(self, b, c, p=None):
        self.b = b
        self.c = c
        self.p = p
    
    # Returns boolean value for if the point is on the curve
    def is_point(self, pt):
        if pt.is_inf:
            return True
        if self.p is None:
            return (pow(pt.y, 2) == pow(pt.x, 3) + self.b * pt.x + self.c)
        else:
            return (pow(pt.y, 2, self.p) == 
                    (pow(pt.x, 3) + self.b * pt.x + self.c) % self.p)
    
    # adds two points on the curve together
    def add(self, pt1, pt2):
        # Check that points are on curve
        #print('I am adding ' + str(pt1) + str(pt2))
        if not self.is_point(pt1) or not self.is_point(pt2):
            raise ValueError('The points being added are invalid.')
        
        # Consider infinity cases 
        if pt1.is_inf and pt2.is_inf:
            return Point(None, None, is_infinity=True)
        if pt1.is_inf:
            return Point(pt2.x, pt2.y)
        if pt2.is_inf:
            return Point(pt1.x, pt1.y)
        if pt1.x == pt2.x and pt1.y != pt2.y:
            return Point(None, None, is_infinity=True)
        
        # Add points otherwise
        if self.p is None:
            if pt1.x == pt2.x and pt1.y == pt2.y:
                if pt1.y == 0:
                    return Point(None, None, is_infinity=True)
                m = (3 * pow(pt1.x, 2) + self.b) / (2 * pt1.y)
            else:
                m = (pt2.y - pt1.y) / (pt2.x - pt1.x)
            x_3 = pow(m, 2) - pt1.x - pt2.x
            y_3 = (m * (pt1.x - x_3)) - pt1.y
            return Point(x_3, y_3)
        else:   # Mod p
            if pt1.x == pt2.x and pt1.y == pt2.y:
                if pt1.y == 0:
                    return Point(None, None, is_infinity=True)
                m = (3 * pow(pt1.x, 2) + self.b) 
                m = (m * DRP.inverse((2 * pt1.y), self.p)) % self.p
            else:
                m = (pt2.y - pt1.y)
                #print('flag')
                #print(DRP.inverse((pt2.x - pt1.x), self.p) % self.p)
                m = (m * DRP.inverse((pt2.x - pt1.x), self.p)) % self.p
                #print(m)
            x_3 = (pow(m, 2) - pt1.x - pt2.x) % self.p
            y_3 = ((m * (pt1.x - x_3)) - pt1.y) % self.p
            return Point(x_3, y_3)

    # Pohlig-Hellman analog
    def pohlig_hellman(self, A, B):
        if not self.is_point(A) or not self.is_point(B):
            raise ValueError('The points are not valid.')
        # First, find smallest integer n so that nA = inf
        n = self.find_n(A)
        # Next, Pohlig-Hellman analog
        primes = DRP.prime_factors(n)
        CRT_dict = {}
        for prime, power in primes.items():
            exp = 1
            x_list = []
            B_sub = B
            while exp <= power:
                q = int(n / pow(prime, exp))
                Bpow = self.check_discrete_log_ans(q, B_sub)
                apow = self.check_discrete_log_ans(int(n / prime), A)
                k = 1
                found = False
                while not found:
                    if self.check_discrete_log_ans(k, apow).equals(Bpow):
                        x_list.append(k)
                        found = True
                    if not found:
                        k = k + 1
                if exp != power:
                    B_sub = self.add(B_sub, self.check_discrete_log_ans(pow(prime, exp-1)*k, self.inverse(A)))
                exp = exp + 1
            exp = 0
            ans_mod_prime = 0
            while exp < power:
                ans_mod_prime = ans_mod_prime + (pow(prime, exp) * x_list[exp])
                exp = exp + 1    
            CRT_dict[ans_mod_prime % pow(prime, power)] = pow(prime, power)
        return DRP.CRT(CRT_dict)

    # smallest int st nA = inf
    def find_n(self, A):
        n = 1
        A_aux = A
        while True:
            if A_aux.is_inf:
                break
            A_aux = self.add(A_aux, A)
            n = n + 1
        return n

    # inverse of point (assume A on curve)
    def inverse(self, A):
        if A.x == 0 or A.y == 0:
            return A
        else:
            return Point(A.x, (-A.y % self.p))
            
    
    # Check a k value by returning point B s.t. B = kA
    def check_discrete_log_ans(self, k, A):
        if k == 0:
            return Point(None, None, true)
        original_A, ans, i = Point(A.x, A.y, A.is_inf), A, 1
        while i < k:
            ans = self.add(ans, original_A)
            i = i + 1
        return ans
    
# Class for a point. Supports infinity
class Point:
    def __init__(self, x, y, is_infinity=False):
        self.x = x
        self.y = y
        self.is_inf = is_infinity
        if is_infinity:
            self.coordinate = None

    def point_mod(self, new_mod):
        return Point(self.x % new_mod, self.y % new_mod, self.is_inf)

    def equals(self, pt):
        return self.x == pt.x and self.y == pt.y and self.is_inf == pt.is_inf
    
    def __str__(self):
        if self.is_inf:
            return 'inf'
        else:
            return '(' + str(self.x) + ', ' + str(self.y) + ')'

if __name__ == '__main__':
    # Working on regular elliptic curve
    # Example p. 350
    ec = Elliptic_Curve(0, 73)
    pt1 = Point(2, 9)
    print(ec.is_point(pt1))
    pt2 = Point(3, 10)
    pt3 = ec.add(pt1, pt2)
    print(pt3)
    print(ec.add(pt3, pt3))
    inf = Point(None, None, True)
    print(ec.add(pt1, inf))
    
    # Working on elliptic curve mod 5
    # Found on p. 352
    ec_mod = Elliptic_Curve(4, 4, 5)
    pt1 = Point(1, 2)
    pt2 = Point(4, 3)
    pt3 = Point(3, 2)
    print(ec_mod.is_point(pt1)) # Should be on
    print(ec_mod.is_point(pt2)) # Should be on
    print(ec_mod.is_point(pt3)) # Should not be on
    print(ec_mod.is_point(inf)) # Should be on
    print(ec_mod.add(pt1, pt2))

    # Example p. 353
    ec_mod = Elliptic_Curve(4, 4, 2773)
    pt = Point(1, 3)
    print(ec_mod.add(pt, pt))

    # My test
    ec = Elliptic_Curve(2, 7, 15)
    pt1 = Point(2, 7)
    print(ec.is_point(pt1))
    ans = ec.add(pt1, ec.add(pt1, pt1))
    print(ans)
    ec3 = Elliptic_Curve(2, 7, 3)
    pt1_3 = pt1.point_mod(3)
    print(ec3.is_point(pt1_3))
    ans_3 = ans.point_mod(3)
    print(ec3.is_point(ans_3))
    ec5 = Elliptic_Curve(2, 7, 5)
    pt1_5 = pt1.point_mod(5)
    print(ec5.is_point(pt1_5))
    ans_5 = ans.point_mod(5)
    print(ec5.is_point(ans_5))
    
    # So, I can break apart an elliptic curve mod pq into mod p and mod q
    #print(ec3.check_discrete_log_ans(3, pt1_3)) # k_1 = 3
    #print(ec5.check_discrete_log_ans(2, pt1_5)) # k_2 = 2

    
    #CRT_dict = {}
    #CRT_dict[0] = 3
    #CRT_dict[2] = 5
    #print(DRP.CRT(CRT_dict))
    # The answer is incorrect and the above code has proven nothing

    ec = Elliptic_Curve(2,3,19) # prime p is important (19)
    print(ec.add(Point(1,5), Point(12,8)))
    print('begin')
    print(ec.check_discrete_log_ans(4, Point(1,5)))
    print('here')
    print(DRP.inverse(-11, 19))
    print(ec.find_n(Point(1,5)))
    #print(ec.pohlig_hellman(Point(1,5),Point(10,7))) # Should equal 4

    print('Testing find n')
    ec = Elliptic_Curve(1,3,5)
    print(ec.add(Point(4,4), Point(4,1)))
    print(ec.find_n(Point(4,1)))
    print()
    
    print('Sample ec')
    ec = Elliptic_Curve(4,4,5)
    print(ec.find_n(Point(4,3)))

    print()
    print('mod 7 example')
    ec = Elliptic_Curve(4,4,7)
    print(ec.find_n(Point(0,2)))
    print(ec.find_n(Point(0,5)))
    print(ec.find_n(Point(1,3)))
    print(ec.find_n(Point(1,4)))
    print(ec.find_n(Point(3,1))) # n = 10
    print(ec.find_n(Point(3,6)))
    print(ec.find_n(Point(4,0)))
    print(ec.find_n(Point(5,3)))
    print(ec.find_n(Point(5,4)))

    print()
    print('mod 7 pohlig hellman')
    print(ec.check_discrete_log_ans(7, Point(3,1)))
    # so, 7(3,1) = (0,5)
    print(ec.check_discrete_log_ans(2, Point(5,3)))
    print(ec.check_discrete_log_ans(2, Point(3,1)))
    print(ec.pohlig_hellman(Point(3,1), Point(0,5)))    #answer should be 7

    print()
    print('Computer Problem 1')
    ec = Elliptic_Curve(2,3,19)
    print(ec.pohlig_hellman(Point(1,5), Point(9,3))) # should be 5
    print(ec.check_discrete_log_ans(5, Point(1,5)))

    # Next need to find a quicker way to find n, because going through all
    # possible values is what the algorithm is built to avoid.
    
    




    
    

