import random

class Bus:
    def __init__(self, ram, *cpus):
        self.ram = ram
        self.cpus = [cpu for cpu in cpus]

        for cpu in self.cpus:
            cpu.ack_bus(self)

    def signal(self, initiator, msg):  # puts signal on the CPU internal bus
        print(f"Signal {msg} put on bus")

        responses = []

        for cpu in self.cpus:
            if cpu is not initiator:
                res = cpu.snoop(initiator, msg)
                responses.append(res)  # each CPU snoops the bus to see the signal

                if res == "modified":
                    # write modified line to RAM
                    self.ram.write(cpu.cache.lines[cpu.cache.tags.index(msg["blk_addr"])], msg["blk_addr"] // self.ram.blk_size)

                    # send modified line to initiating cache
                    return [res, cpu.cache.lines[cpu.cache.tags.index(msg["blk_addr"])]]

        if msg["op"] == "read miss":
            if "shared" in responses:
                return "shared"
            else:
                return None
        elif msg["op"] == "rwitm":
            return None


class CPU:
    def __init__(self, cache, ram):
        self.cache = cache
        self.ram = ram
        self.cache_fifo = 0  # keeps track of the "oldest" FIFO line

    def read(self, addr: int, rwitm=False):
        word = self.cache.read(addr)

        if word == None:
            print("RM" if not rwitm else "WM")

            blk_addr, block = self.ram.read(addr)

            # put signal on bus and receive response from snooping CPUs
            signal = {"op": "read miss" if not rwitm else "rwitm", "blk_addr": blk_addr}
            signal_res = self.bus.signal(self, msg=signal)
            print(f"Bus returned {signal_res}")

            # if modified, block RAM read and receive line from other cache via bus
            try:
                if "modified" in signal_res:
                    if not rwitm:
                        block = signal_res[1]
                    else:
                        blk_addr, block = self.ram.read(addr)

                        signal = {"op": "read miss" if not rwitm else "rwitm", "blk_addr": blk_addr}
                        signal_res = self.bus.signal(self, msg=signal)
                        print(f"Signal {signal} put on bus, returned {signal_res}")
            except TypeError:  # exception for if no signal is returned from the bus
                pass

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

            # try-catch is just in case signal_res is NoneType
            print(f"BEFORE: {self.cache.mesi_states[self.cache.tags.index(blk_addr)]}")
            try:
                if rwitm:
                    self.cache.mesi_states[self.cache.tags.index(blk_addr)] = "modified"
                elif signal_res == "shared":
                    self.cache.mesi_states[self.cache.tags.index(blk_addr)] = "shared"
                elif not signal_res:
                    self.cache.mesi_states[self.cache.tags.index(blk_addr)] = "exclusive"
                elif "modified" in signal_res:
                    self.cache.mesi_states[self.cache.tags.index(blk_addr)] = "shared"
            except TypeError:
                pass
            print(f"AFTER: {self.cache.mesi_states[self.cache.tags.index(blk_addr)]}")

            if self.cache.free_line != None:
                if self.cache.free_line == self.cache.size // self.cache.line_size - 1:
                    self.cache.free_line = None
                else:
                    self.cache.free_line += 1

            word = self.cache.read(addr)
        else:
            print("RH" if not rwitm else "WH")

            if rwitm:
                self.bus.signal(self, msg={"op": "rwitm", "blk_addr": addr // self.ram.blk_size * self.ram.blk_size})

        return word

    def read_modify(self, data: int, addr: int):
        word = self.read(addr, rwitm=True)

        self.cache.modify(data, addr)

        return word

    # snoops a transaction on the bus
    def snoop(self, initiator, msg):
        line = msg

        if msg["op"] == "read miss":
            if msg["blk_addr"] in self.cache.tags:
                print(f"Snooper from {self.cache.mesi_states[self.cache.tags.index(msg['blk_addr'])]}", end=""),

                if self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] == "exclusive":
                    self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] = "shared"

                    print(f" to shared")

                    return "shared"
                elif self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] == "shared":
                    print(f" to shared")

                    return "shared"
                elif self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] == "modified":
                    self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] = "shared"

                    print(f" to shared")

                    return "modified"
            else:  # no signal is sent to the bus
                return None
        if msg["op"] == "rwitm":
            if msg["blk_addr"] in self.cache.tags:
                print(f"Snooper from {self.cache.mesi_states[self.cache.tags.index(msg['blk_addr'])]}", end="")

                if self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] == "modified":
                    self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] = "invalid"

                    print(f" to invalid")

                    return "modified"
                elif self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] != "invalid":
                    self.cache.mesi_states[self.cache.tags.index(msg["blk_addr"])] = "invalid"

                    print(f" to invalid")

                    return None
            else:
                return None


    # registers a bus for MESI signals and snooping
    def ack_bus(self, bus):
        self.bus = bus


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

    def __str__(self):  # representation of current RAM state
        s = "\n----- Main memory -----\n"

        s += "| block | addr | data |\n"

        for i in range(len(self.memory) // self.blk_size):  # for block
            blk = ""

            for j in range(self.blk_size):  # for word in block
                blk += f"{self.memory[i * self.blk_size + j]:03} "

            s += f"| {i:03} | {i * self.blk_size:04} | {blk}|\n"

        s += "| block | addr | data |"

        return s


class Cache:
    def __init__(self, size: int, line_size: int):
        self.size = size
        self.line_size = line_size
        self.lines = []  # actual memory space
        self.tags = []  # RAM addresses
        self.dirty_bits = []  # flags for if line has to be written back
        self.free_line = 0  # keeps track of empty lines
        self.mesi_states = []  # MESI state for each line

        # initializes empty cache tags, lines, counters, and flags
        for i in range(size // line_size):
            self.tags.append(None)
            self.lines.append([None for j in range(self.line_size)])
            self.dirty_bits.append(False)
            self.mesi_states.append("invalid")

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

    def __str__(self):  # representation of current cache state
        s = "\n----- Cache -----\n"

        s += "| line |   data   | tag | dirty bit | MESI state\n\n"

        for n, line in enumerate(self.lines):
            s += f"| {n} | {line} | {self.tags[n]} | {self.dirty_bits[n]} | {self.mesi_states[n]}\n"

        return s
