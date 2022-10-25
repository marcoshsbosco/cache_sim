import components
import random

ram = components.RAM(size=1024, blk_size=2)
cache1 = components.Cache(size=16, line_size=2)
cache2 = components.Cache(size=16, line_size=2)
cache3 = components.Cache(size=16, line_size=2)
cache4 = components.Cache(size=16, line_size=2)
cpu1 = components.CPU(cache1, ram)
cpu2 = components.CPU(cache2, ram)
cpu3 = components.CPU(cache3, ram)
cpu4 = components.CPU(cache4, ram)
cpu_bus = components.Bus(ram, cpu1, cpu2, cpu3, cpu4)

def access(cpu, acc_type, addr):
    print(f"\n-----Requesting {acc_type} at address {addr}-----")

    if acc_type == "read":
        print(f"Word: {cpu.read(addr)}\n")
    else:
        new_data = random.randint(0, 255)
        print(f"Word: {cpu.read_modify(new_data, addr)}\n")

def menu():
    print("-----Main menu-----")
    print("1. Print RAM")
    print("2. Choose CPU")
    print("0. Exit program")

    option = input("")
    if option == "1":
        print(f"{ram}\n")

        return
    elif option == "0":
        exit()

    print("\n-----Choose a processor-----")
    print("1. CPU 1")
    print("2. CPU 2")
    print("3. CPU 3")
    print("4. CPU 4")

    cpu = input("")

    print("\n-----Choose an action-----")
    print("1. Read")
    print("2. Modify")
    print("3. Print cache")

    option = input("")

    if option != "3":
        acc_type = "read" if option == "1" else "read_modify"

        print(f"\n-----Type an address (0 to {len(ram.memory) - 1})-----")
        addr = int(input(""))

        access(eval(f"cpu{cpu}"), acc_type, addr)
    else:
        print(eval(f"cpu{cpu}.cache"))

while True:
    menu()
