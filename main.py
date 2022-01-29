import math
import random
import re
import time


class IO:
    @classmethod
    def init(cls, num):
        cls.num = num
        cls.o = open(f'output{cls.num}.stock', 'w')

    @classmethod
    def read(cls):
        with open(f'input{cls.num}.stock') as f:
            t = f.read()
        return t

    @classmethod
    def print(cls, t='', to_file=False):
        print(t)
        if to_file:
            cls.o.write(str(t) + '\n')


class Stock:
    def __init__(self, length=None):
        if length is not None:
            self.__free_length = length
            self.__cuts = []

    def add(self, length):
        if self.__free_length >= length:
            self.__free_length -= length
            self.__cuts.append(length)
        else:
            raise Exception('insufficient free length')

    def remove(self, index):
        self.__free_length += self.__cuts[index]
        self.__cuts.remove(self.__cuts[index])

    def empty(self):
        return not self.__cuts

    def transfer_a_cut_to(self, other):
        cut_index = random.randrange(len(self.__cuts))
        try:
            other.add(self.__cuts[cut_index])
            self.remove(cut_index)
            return True
        except:
            return False

    def copy(self):
        new = Stock()
        new.__free_length = self.__free_length
        new.__cuts = self.__cuts.copy()
        return new

    def __str__(self):
        return ' '.join(map(str, self.__cuts)) + '\n'

    def __repr__(self):
        return self.__str__()


class Answer:
    def __init__(self, length=None, requests=None):
        if length is not None and requests is not None:
            self.length = length
            self.__stocks = []
            indexes = list(range(len(requests)))
            random.shuffle(indexes)
            for i in indexes:
                try:
                    self.__stocks[-1].add(requests[i])
                except:
                    self.__stocks.append(Stock(length))
                    self.__stocks[-1].add(requests[i])

    def copy(self):
        new = Answer()
        new.length = self.length
        new.__stocks = [stock.copy() for stock in self.__stocks]
        return new

    def stocks_count(self):
        return len(self.__stocks)

    def mutate(self, degree):
        count = random.randint(1, degree)
        new = self.copy()
        while count > 0:
            if random.random() > 1 / self.stocks_count():
                stock_0, stock_1 = random.choices(new.__stocks, k=2)
            else:
                stock_0 = random.choice(new.__stocks)
                stock_1 = Stock(new.length)
                new.__stocks.append(stock_1)

            if stock_0.transfer_a_cut_to(stock_1):
                count -= 1
            if stock_0.empty():
                new.__stocks.remove(stock_0)
            if stock_1.empty():
                new.__stocks.remove(stock_1)
        return new

    def __str__(self):
        return 'Number of Stocks: ' + str(self.stocks_count()) + '\n' + 'Stocks:\n' + ''.join(map(str, self.__stocks)) + '\n'


# Read length and requests from input file
NUM = 1
IO.init(NUM)
raw_input = IO.read()

length = int(re.findall(r'Stock Length:\s*(\d+)', raw_input)[0])
requests = list(map(int, re.findall(r'Requests:((\s*\d+,)*\s*(\d+)?)', raw_input)[0][0].split(',')))


# Run the Simulated Annealing
start = time.time()


def TEMPERATURE(iteration, chaos): return .99 ** (iteration / 100) * chaos


MUTATION_DEGREE = 20
STAGNANCY_THRESHOLD = 5000

stagnancy = 0
current = Answer(length, requests)
best = current
last = current
iteration = 0
chaos = 1
while True:
    temperature = TEMPERATURE(iteration, chaos)
    IO.print(f'{iteration}\t{current.stocks_count()}\t{temperature}')
    iteration += 1
    new = current.mutate(MUTATION_DEGREE)
    delta = new.stocks_count() - current.stocks_count()
    if delta < 0 or random.random() < math.exp(-delta/temperature):
        current = new

    if last.stocks_count() == current.stocks_count():
        stagnancy += 1
        chaos += .01
    else:
        stagnancy = 0
    if stagnancy > STAGNANCY_THRESHOLD:
        break
    last = current

    if current.stocks_count() < best.stocks_count():
        best = current


IO.print()
IO.print(best, True)
IO.print(f'Iterations: {iteration}', True)
IO.print(f'Time: {time.time() - start}', True)

IO.o.close()
