from os import urandom
import hashlib
from sys import argv
import base64


# returns a hash
def hashit(pw, alg, numiter, salt):
    m = hashlib.new(alg)
    tohash = pw
    for i in range(0, int(numiter)):
        m.update(tohash)
        m.update(salt)
        tohash = m.digest()
    del pw
    return m.hexdigest()

# returns salt:iter:alg:hash
def get_hashstr(pw, alg, numiter, salt=urandom(10)):
    hash = hashit(pw, alg, numiter, salt)
    return ':'.join([base64.b64encode(salt), str(numiter), alg, hash])

# hashes the given password with the specifics in hashstr and compares it agains the generated hash
def compare(pw, hashstr):
    salt, numiter, alg, h = hashstr.split(':')
    if hashit(pw, alg, numiter, base64.b64decode(salt)) == h:
        return True
    return False

class PassPolicy(object):

    def __init__(self, lower=0, upper=0, digits=0, syms=0, length=0, classes=1):
        self.lower = lower
        self.upper = upper
        self.digits = digits
        self.syms = syms
        self.length = length
        self.classes = classes
        self.errors = list()

    def checkpw(self, pw):
        del self.errors[:]
        digits = sum(x.isdigit() for x in pw)
        lower = sum(x.islower() for x in pw)
        upper = sum(x.isupper() for x in pw)
        length = len(pw)
        syms = length - digits - lower - upper
        classes = (digits>0) + (lower>0) + (upper>0) + (syms>0)
        if length < self.length:
            self.errors.append("Password not long enough. (Must be {} characters long)".format(self.length))
        if classes < self.classes:
            self.errors.append("Password does not have enough character classes. (Must have {} classes)".format(self.classes))
        if digits < self.digits:
            self.errors.append("Not enough digits. (Need {} had {})".format(self.digits, digits))
        if upper < self.upper:
            self.errors.append("Not enough capital letters. (Need {} had {})".format(self.upper, upper))
        if lower < self.lower:
            self.errors.append("Not enough lowercase letters. (Need {} had {})".format(self.lower, lower))
        if syms < self.syms:
            self.errors.append("Not enough symbols. (Need {} had {})".format(self.syms, syms))
        if len(self.errors):
            return False
        return True

if __name__ == '__main__':
    policy = PassPolicy(3, 4, 1, 1, 5, 2)
    if not policy.checkpw(argv[1]):
        print "Requirements not met"
        print policy.errors
    hashstr = get_hashstr(argv[1], 'sha512', 100000)
    print hashstr
