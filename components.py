import random

class CPU:
    def __init__(self, cache, ram):
        self.cache = cache
        self.ram = ram
        self.cache_fifo = 0  # keeps track of the "oldest" FIFO line

    def read(self, addr: int):
        word = self.cache.read(addr)

        if word == None:
            print("Miss")

            blk_addr, block = self.ram.read(addr)

            if self.cache.free_line == None:  # use a replacement algorithm
                print("No free lines in cache, using FIFO replacement algorithm")

                line = self.cache_fifo  # line to be replaced
                if self.cache_fifo < self.cache.size // self.cache.line_size - 1:
                    self.cache_fifo = self.cache_fifo + 1
                else:  # set "oldest" element back to 0 if FIFO is at the end of the cache
                    self.cache_fifo = 0

            else:  # direct map
                print("Free line found in cache")
                line = self.cache.free_line

            # write back
            if self.cache.dirty_bits[line]:
                print(f"Dirty bit, writing line {line} back to block {self.cache.tags[line] // self.ram.blk_size}")

                self.ram.write(self.cache.lines[line], self.cache.tags[line] // self.ram.blk_size)
                self.cache.dirty_bits[line] = False

            self.cache.write(block, blk_addr, line)

            if self.cache.free_line != None:
                if self.cache.free_line == self.cache.size // self.cache.line_size - 1:
                    self.cache.free_line = None
                else:
                    self.cache.free_line += 1

            word = self.cache.read(addr)
        else:
            print("Hit")

        return word

    def read_modify(self, data: int, addr: int):
        word = self.read(addr)

        self.cache.modify(data, addr)

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
        self.dirty_bits = []  # flags for if line has to be written back
        self.free_line = 0  # keeps track of empty lines

        # initializes empty cache tags, lines, counters, and flags
        for i in range(size // line_size):
            self.tags.append(None)
            self.lines.append([None for j in range(self.line_size)])
            self.dirty_bits.append(False)

    def read(self, addr: int):
        blk = addr // self.line_size
        blk_addr = blk * self.line_size

        if blk_addr in self.tags:  # hit
            line = self.tags.index(blk_addr)

            print(f"Reading from line {line}")

            return self.lines[line][addr % self.line_size]  # returns word
        else:  # miss
            return None

    def write(self, data: list, tag: int, line: int):
        print(f"Writing to line {line}")

        self.tags[line] = tag
        self.lines[line] = data

    def modify(self, data: int, addr: int):
        print(f"Writing {data} to {addr}")

        blk = addr // self.line_size
        blk_addr = blk * self.line_size

        line = self.tags.index(blk_addr)

        self.lines[line][addr % self.line_size] = data
        self.dirty_bits[line] = True
