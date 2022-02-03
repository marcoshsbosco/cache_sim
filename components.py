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
    pass
