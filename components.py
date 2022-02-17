import random

class CPU:
    def __init__(self, cache, ram, replacement):
        self.replacement = replacement
        self.cache = cache
        self.ram = ram

    def read(self, addr: int):
        word = self.cache.read(addr)

        if word == None:
            print("\nMiss")

            blk_addr, block = self.ram.read(addr)

            if self.replacement == "random":
                line = random.randint(0, self.cache.size // self.cache.line_size - 1)

            self.cache.write(block, blk_addr, line)
            word = self.cache.read(addr)
        else:
            print("\nHit")

        return word

class RAM:
    def __init__(self, size: int, blk_size: int):
        self.blk_size = blk_size
        self.memory = []  # actual memory space

        # initialize each RAM word with a random integer
        for i in range(size):
            self.memory.append(random.randint(0, 255))

    def write(self, data: list, blk: int):
        blk_addr = blk * self.blk_size

        self.memory[blk_addr : blk_addr + self.blk_size] = data

    def read(self, addr: int):
        blk = addr // self.blk_size
        blk_addr = blk * self.blk_size

        print(f"Block number: {blk}")  # DEBUG
        print(f"Block address: {blk_addr}")  # DEBUG

        return blk_addr, self.memory[blk_addr:blk_addr + self.blk_size]  # returns block that contains addr and its address


class Cache:
    def __init__(self, size: int, line_size: int):
        self.size = size
        self.line_size = line_size
        self.lines = []  # actual memory space
        self.tags = []  # RAM addresses

        # initializes empty cache tags and lines
        for i in range(size // line_size):
            self.tags.append(None)
            self.lines.append([None for j in range(self.line_size)])

    def read(self, addr: int):
        blk = addr // self.line_size
        blk_addr = blk * self.line_size

        if blk_addr in self.tags:  # hit
            return self.lines[self.tags.index(blk_addr)][addr % self.line_size]  # returns word
        else:  # miss
            return None

    def write(self, data: list, tag: int, line: int):
        self.tags[line] = tag
        self.lines[line] = data
