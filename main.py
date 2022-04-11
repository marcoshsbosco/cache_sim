import components

ram = components.RAM(size=1024, blk_size=2)
cache = components.Cache(size=16, line_size=2)
cpu = components.CPU(cache, ram, replacement="random")

print(f"Word: {cpu.read(0)}\n")
print(f"Word: {cpu.read(1)}\n")
print(f"Word: {cpu.read(2)}\n")
