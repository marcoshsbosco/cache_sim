import random

class RAM:
    def __init__(self, size: int, blk_size: int):
        self.blk_size = blk_size
        self.memory = []  # actual memory space

        # initialize each RAM word with a random integer
        for i in range(size):
            self.memory.append(random.randint(0, 255))

    # writes a block of data to RAM
    def write(self, data: list, blk: int):
        blk_addr = blk * self.blk_size  # block's memory address in RAM

        self.memory[blk_addr : blk_addr + self.blk_size] = data

    def read(self, addr: int):
        blk = addr // self.blk_size  # block number which addr is in
        blk_addr = blk * self.blk_size  # block address

        print(f"Block number: {blk}")  # DEBUG
        print(f"Block address: {blk_addr}")  # DEBUG

        return self.memory[blk_addr:blk_addr + self.blk_size]  # returns block that contains addr


class Cache:
    def __init__(self, size: int, line_size: int):
        self.size = size
        self.line_size = line_size
        self.lines = []
        self.tags = []

        for i in range(size // line_size):
            self.tags.append(None)
            self.lines.append([None for j in range(self.line_size)])

    def read(self, addr: int):
        blk = addr // self.line_size
        blk_addr = blk * self.line_size

        if blk_addr in self.tags:
            return self.lines[self.tags.index(blk_addr)][addr % self.line_size]
        else:
            return None

    def write(self, data: list, tag: int, replacement):
        if replacement == "random":
            line = random.randint(0, self.size // self.line_size - 1)

            print(f"\nLine number: {line}")  # DEBUG

            self.tags[line] = tag
            self.lines[line] = data

            print(f"Cache: {self.lines}")  # DEBUG
            print(f"Tags: {self.tags}")  # DEBUG
