''' Partition a list into sublists whose sums don't exceed a maximum 
    using a First Fit Decreasing algorithm. See
    http://www.ams.org/new-in-math/cover/bins1.html
    for a simple description of the method.
'''

    
class Bin(object):
    ''' Container for items that keeps a running sum '''
    maxSize = 0
    def __init__(self, name, value):
        self.names = [name]
        self.sum = value
    
    def add_value(self, name, value):
        can_add = self.sum + value <= Bin.maxSize
        if can_add:
            self.sum += value
            self.names.append(name)
        return can_add

    def __str__(self):
        ''' Printable representation '''
        return 'Bin(sum=%d, items=%s)' % (self.sum, str(self.names))

    def __index__(self, i):
        return self.names[i]

    def __iter__(self):
        return iter(self.names)

def pack(values, maxValue):
    values = sorted(values, key=lambda tup: tup[1], reverse=True)
    bins = []
    Bin.maxSize = maxValue
    for name, value in values:
        for bin in bins:
            if bin.add_value(name, value):
                break
        else:
            bins.append(Bin(name, value))
    
    return bins

