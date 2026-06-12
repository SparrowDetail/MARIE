# MARIE

This is currently a console based package designed to simulate the assembly, execution, and memory processes displayed in the MARIE Simple Computer example. The project was picked up as a fun portfolio project after a simplistic version was designed for my Computer Architecture course during my undergrad. Some practical enhancements are planned to role out as development continues, view [here](#planned-enhancements).

To get started, view [Install from this REPO](#install-from-this-repo) and [Basic Example](#basic-example).

## Install from this REPO

Recommended to avoid a global installation by installing within your chosen virtual environment, such as [venv](https://docs.python.org/3/library/venv.html).

You can install from this repository using pip with the following command:

```pip install MARIE@git+https://github.com/SparrowDetail/MARIE.git```

Feel free to use the package anyway you see fit and star the repo to stay in touch. See [Planned Enhancements](#planned-enhancements) for future enhancements.

## Basic Example

At its core, this package is composed of three basic components. First, the Memory class that essentially acts as an array of 4096 addresses (MARIE example has a 4096 byte memory) with a basic formatted print function and store/load functions for addressing. Next, the Assembler class that will read a file containing MARIE assembly code and assemble it into memory. Lastly, the Marie class that can execute an assembled program stored in memory, simulating the internal architecture of the MARIE CPU.

Now, before you can run your MARIE simulation, you will need a program written in MARIE assembly language. Below is a basic program that will output the addition of two integers named `addition.asm`. You can learn more about the MARIE Assembly language with [this document](https://www.cs.uni.edu/~fienup/cs041s11/lectures/Supplement_MARE_AL.pdf) from the University of Northern Iowa.

```assembly
/ Contents of addition.asm
input
store temp
input

add temp
output
halt

temp, DEC 0
```

Next, your basic execution will require an instance of the Assembly class and the Marie class. An assembly object will contain a Memory object that can be passed directly into a Marie object at initialization or by accessing the Marie objects internal memory variable, like so `marie_object.memory = memory_object`. From here, you have two primary execution function: `marie_object.execute()` that runs the program from memory and returns the outputs and `marie_object.executeStepwise()` which executes the program while pausing at each step to display the current memory state and register actions in Register Transfer Notation (RTN). Below is a basic script that would assemble and execute the `addition.asm` file stepwise.

```Python
from MARIE import Assembler,Marie

assembler = Assembler()
assembler.assembleFile('addition.asm') #Searches file subtree from current directory

marie = Marie(assembler.memory)
marie.executeStepwise()
```

## Planned Enhancements

This package began as a simple practical example assigned in my Computer Architecture course during my undergrad. I decided to pick it up again as a fun portfolio project after graduation, so hopefully it can see some practical use as development expands. Below is a list of planned enhancements coming in the near future:

- implement a proper test branch using pytest
- include some unique MARIE assembly code examples
- build an interactive web app interface using Reflex
- general formatting and documentation improvements (comply with the pythonic standards)
