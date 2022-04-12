import components
import random

def random_access(quantity: int):
    for i in range(quantity):
        addr = random.randint(0, len(ram.memory) - 1)
        print(f"-----Requesting read at address {addr}-----")
        print(f"Word: {cpu.read(addr)}\n")

ram = components.RAM(size=1024, blk_size=2)
cache = components.Cache(size=16, line_size=2)
cpu = components.CPU(cache, ram, replacement="random")

random_access(quantity=32)
