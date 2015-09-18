class Complex:
    def __init__(self, r, i):
        self.real = r
        self.imag = i
    def add(self, c):
        self.real += c.real
        self.imag += c.imag
    def mult(self, c):
        r = self.real*c.real - self.imag*c.imag
        self.imag = c.real*self.imag + self.real*c.imag
        self.real = r
    def _print(self):
        print self.real, "+", self.imag, "i"

class FancyComplex(Complex):
    
x = Complex(0, 1)
y = Complex(0, 1)
x.mult(y)
x._print()
