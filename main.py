import components

ram = components.RAM(size=1024, blk_size=2)
cache = components.Cache(size=16, line_size=2)

print("----- Reading from RAM address 5 -----")
print(f"Block: {ram.read(5)}\n")

print("----- Writing [69, 420] to block number 2 -----\n")
ram.write([69, 420], 2)

print("----- Reading from RAM address 5 -----")
print(f"Block: {ram.read(5)}\n")

print("----- Writing block 2 to cache -----")
cache.write(ram.read(5), 4, "random")

print("\n----- Reading RAM address 5 from cache -----")
print(f"Word: {cache.read(5)}\n")
