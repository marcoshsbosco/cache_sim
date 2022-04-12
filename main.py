import components
import random

def random_access(quantity: int):
    for i in range(quantity):
        access = random.choice(["read", "read_modify"])
        addr = random.randint(0, len(ram.memory) - 1)
        print(f"-----Requesting {access} at address {addr}-----")

        if access == "read":
            print(f"Word: {cpu.read(addr)}\n")
        else:
            new_data = random.randint(0, 255)
            print(f"Word: {cpu.read_modify(new_data, addr)}\n")

ram = components.RAM(size=1024, blk_size=2)
cache = components.Cache(size=16, line_size=2)
cpu = components.CPU(cache, ram, replacement="random")

random_access(quantity=32)
