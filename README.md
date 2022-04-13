# Cache memory simulator
This program simulates how cache memory works and interacts with the processor and main memory of a computer.

## Instructions
### Running the program
Open a terminal in the main directory, type `make` and press Enter.

### Component parameters
Lines 16 through 18 of `main.py` contain the constructors for the components to be simulated. There, you can change RAM memory and block size, cache memory and line size, and CPU replacement algorithm (`lfu` or `random`).
At line 20, you may change the quantity of random accesses generated and sent to the CPU.

### Manual memory accesses
Instead of random accesses using the `random_access` function, you may opt to manually issue commands to the CPU.

- `cpu.read(addr: int)`

Retrieves the word located at address `addr` of main memory. Inserting this method in a `print` call prints the word to the terminal.

- `cpu.read_modify(new_data: int, addr: int)`

Retrieves the word located at address `addr` of main memory. Inserting this method in a `print` call prints the word to the terminal. After reading the word from memory, this function also overwrites `new_data` to address `addr` of main memory.
