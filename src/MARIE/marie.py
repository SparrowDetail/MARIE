# MARIE object deffinition, including a general execution utility and educational,
# stepwise utility.
#
# Author: Steven Short
# Professor: Abdulbast Abushgra
# Date: 4/18/2025
# Revised: 2/26/2026

from .memory import Memory
import os

class Marie():
    '''
    Marie class that simulates internal architecture of the Marie Simple Computer example. Requires a pointer to an assembled
    program in a Memory object to execute the program.

    Attributes:
        ac (int): Accumulator (16-bit) register that stores arithmetic logic and results.
        mar (int): Memory Address Register (12-bit) stores specific memory addresses being read or written to.
        mbr (int): Memory Buffer Register (16-bit) stores data read from memory or preparing to be written to memory.
        pc (int): Program Counter (12-bit) tracks the memory address of the next instruction in memory.
        ir (int): Instruction Register (16-bit) stores the binary instruction currently being executed.
        InReg (int): Input Register (12-bit) stores user inputs.
        OutReg (int): Output Register (12-bit) stores program output values.
        memory (Memory): Memory object containing an assembled MARIE program.

    Methods:
        execute(): Console based method that executes the program and displays outputs in console.
        execute_stepwise(): Console based method that executes the program with descriptive steps in the console.
        get_rtl(target_register,transferring_register,value): Accepts a target and transferring register name and integer value and returns a formatted string in Register Transfer Language (RTL).
    '''
    def __init__(self, mem: Memory = Memory()):
        self.ac = 0x0
        self.mar = 0x0
        self.mbr = 0x0
        self.pc = 0x0
        self.ir = 0x0
        self.InReg = 0x0
        self.OutReg = 0x0
        self.memory = mem
        self.__exit = False
        self.__debug_text = False
        self.__outputs = []
        self.__control = {
            0x0: self.__jns,
            0x1: self.__load,
            0x2: self.__store,
            0x3: self.__add,
            0x4: self.__subt,
            0x5: self.__input,
            0x6: self.__output,
            0x7: self.__halt,
            0x8: self.__skipcond,
            0x9: self.__jump,
            0xA: self.__clear,
            0xB: self.__addi,
            0xC: self.__jumpi
        }
    
    def __str__(self):
        '''
        Str output default, displays Marie registers and simulated memory stored contents.
        '''
        width = 12
        out = ''.ljust(width)
        out += f'AC: {self.ac:04X}'.ljust(width)
        out += f'MAR: {self.mar:04X}'.ljust(width)
        out += f'MBR: {self.mbr:04X}'.ljust(width)
        out += f'PC: {self.pc:04X}'.ljust(width)
        out += f'IR: {self.ir:04X}'.ljust(width)
        out += f'InReg: {self.InReg:04X}'.ljust(width)
        out += f'OutReg: {self.OutReg:04X}'.ljust(width)

        out += f'\n\n{self.memory}'

        return out

    def __initialize(self):
        '''
        MARIE helper method used to re-initialize MARIE registers to default values.
        '''
        self.ac = 0x0
        self.mar = 0x0
        self.mbr = 0x0
        self.pc = 0x0
        self.ir = 0x0
        self.InReg = 0x0
        self.OutReg = 0x0
        self.__exit = False
        self.__outputs = []
    
    def __display_output(self):
        '''
        MARIE helper method used to display output values as hexadecimal or decimal values as prompted by user input.
        '''
        is_hex = True if input('Display output as hexadecimal values (Y/N)?').upper().startswith('Y') else False
        print('\nOutput:')
        for o in self.__outputs:
            if is_hex: 
                print(f'\t0x{o:03X}')
            else:
                print(f'\t{o}')
    
    def get_rtl(self, target_register:str, transferring_register:str, value:int) -> str:
        '''
        Accepts register names and values and returns a string formatted in MARIE Register Transfer LAnguage (RTL) with the 
        transfer value in parenthesis next to the RTL text (MAR ← PC (0x003)). 
        
        The value will be displayed with three hexadecimal digits for 12 bit register transfers and four hexadecimal digits for
        16 bit registers.

        Args:
            target_register (str): First register in RTL format that is receiving data (value copied to).
            transferring_register (str): Second register in RTL format that is sending data (value copied from).
            value (str): Register value being copied as a string
            fourDigitRegister (bool): Optional boolean display modifier that displays the value as a four digit hex number, otherwise display as a three digit number
        
        Examples:
            Return Register Transfer Language:

            >>> Marie.get_rtl("MAR", "PC", 3)
            MAR ← PC (0x003)

            >>> Marie.get_rtl("MBR", "M[MAR]", 10)
            MBR ← M[MAR] (0x000A)
        '''
        sixteen_bit_registers = {'M[MAR]', 'MBR', 'IR', 'AC'}

        if target_register in sixteen_bit_registers:
            formatted_value = formatted_value = f'{value:04X}'
        else:
            formatted_value = f'{value:03X}'

        return f'{target_register} \u2190 {transferring_register} (0x{formatted_value})'
    
    def __print_rtl(self, target_register:str, transferring_register:str, value:int):
        '''
        MARIE helper method used to print register actions in MARIE Register Transfer Language (RTL) format (MAR ← PC (0x003)).
        This method will include the value being passed in parenthesis next to the the RTL text.

        Args:
            target_register (str): First register in RTL format that is receiving data (value copied to).
            transferring_register (str): Second register in RTL format that is sending data (value copied from).
            value (str): Register value being copied as a string
            fourDigitRegister (bool): Optional boolean display modifier that displays the value as a four digit hex number, otherwise display as a three digit number
        
        Examples:
            Print register actions:

            >>> Marie.__print_rtl("MAR", "PC", 3)
                MAR ← PC (0x003)

            >>> Marie.__print_rtl("MBR", "M[MAR]", 10, True)
                MBR ← M[MAR] (0x000A)
        '''
        print(f'\t{self.get_rtl(target_register, transferring_register, value)}')

    def __fetch(self):
        '''
        MARIE helper function that controls register actions for the MARIE fetch instruction. 
        
        If debug text is set to true, will print Register Transfer Language steps to terminal.
        '''
        self.mar = self.pc
        self.mbr = self.memory.load(self.mar)
        self.ir = self.mbr
        self.pc += 1
        if self.__debug_text: 
            print('Fetch:')
            self.__print_rtl('MAR','PC',self.mar)
            self.__print_rtl('MBR', 'M[MAR]', self.mbr)
            self.__print_rtl('IR', 'MBR', self.ir)
            self.__print_rtl('PC', 'PC + 1', self.pc)
    
    def __decode(self):
        '''
        Interprets the data stored within the Instruction Register (IR) based on MARIE instruction set.

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If stored instruction is outside instruction set.
        '''
        inst = (self.ir >> 12) & 0xF
        self.mar = self.ir & 0xFFF
        action = self.__control.get(inst)
        if self.__debug_text:
            print(f'Decode IR[15-12] (0x{inst:X}):')
            self.__print_rtl('MAR','IR[15-12]',self.mar)
        if action:
            action()
        else:
            raise MarieExecutionError(f'critical error, passed instruction outside instruction set (address {self.pc - 1})')
    
    def __add(self):
        '''
        Simulates the addition instruction (add value at MAR address to AC register).

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If target memory block is out of range.
        '''
        try:
            self.mbr = self.memory.load(self.mar)
            self.ac += self.mbr
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debug_text:
            print('ADD:')
            self.__print_rtl('MBR','M[MAR]',self.mbr)
            self.__print_rtl('AC','AC + MBR',self.ac)

    def __subt(self):
        '''
        Simulates the subtract instruction (subtract value at MAR address from AC register).

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If target memory block is out of range.
        '''
        try:
            self.mbr = self.memory.load(self.mar)
            self.ac -= self.mbr
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debug_text:
            print('SUBT:')
            self.__print_rtl('MBR','M[MAR]',self.mbr)
            self.__print_rtl('AC','AC - MBR',self.ac)

    
    def __addi(self):
        '''
        Simulates Marie the add indirect instruction. Uses the address stored at the target address to retrieve a value and add that value to the accumulator (AC) register.

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If any address is out of range.
        '''
        try:
            self.mbr = self.memory.load(self.mar)
            self.mar = self.mbr
            self.mbr = self.memory.load(self.mar)
            self.ac += self.mbr
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debug_text:
            print('ADDI:')
            self.__print_rtl('MBR','M[MAR]',self.mar)
            self.__print_rtl('MAR','MBR',self.mar)
            self.__print_rtl('MBR','M[MAR]',self.mbr)
            self.__print_rtl('AC','AC + MBR',self.ac)
    
    def __clear(self):
        '''
        Sets the AC register to a zeroed state.

        If debug text is set to true, will print Register Transfer Language steps to terminal.
        '''
        self.ac = 0x0
        if self.__debug_text:
            print('CLEAR:')
            self.__print_rtl('AC','0x0',self.ac)
    
    def __load(self):
        '''
        Loads the value at a the address stored within the MAR register.

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If the target address is outside the maximum address range (4096)
        '''
        try:
            self.ac = self.memory.load(self.mar)
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debug_text:
            print('LOAD:')
            self.__print_rtl('AC','M[MAR]',self.ac)
    
    def __store(self):
        '''
        Stores the value of the AC register to the memory address stored within the MAR register

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If the passed address is outside the maximum address range (4096) or the stored value exceeds the maximum memory size (0xFFFF)
        '''
        try:
            self.memory.store(self.ac , self.mar)
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debug_text:
            print('STORE:')
            print(f'\tM[MAR] \u2190 AC ({self.ac:03X})')
    
    def __input(self):
        '''
        Requests and validates user input for Marie input instruction. Validated input stored within Marie Input Register (InReg) and transferred to the 
        Accumulator (AC).

        If debug text is set to true, will print Register Transfer Language steps to terminal.
        '''
        print('User input requested:')
        self.InReg = 0x0
        while True:
            try:
                isHex = True if input('Is the input a hexadecimal value (Y/N)?').upper().startswith('Y') else False
                if isHex:
                    self.InReg = int(input('Enter your input:'), 16)
                else:
                    self.InReg = int(input('Enter your input:'))
                if self.InReg > 0xFFF:
                    raise Exception()
                break
            except ValueError:
                print('Value did not match requested input')
            except Exception:
                print('Improper input, try again')
        self.ac = self.InReg
        if self.__debug_text:
            print('INPUT:')
            self.__print_rtl('InReg','Keyboard',self.InReg)
            self.__print_rtl('AC','InReg',self.ac)
    
    def __output(self):
        '''
        Appends the current value of the accumulator to an internal output array for display at the end of program execution.

        If debug text is set to true, will print Register Transfer Language steps to terminal.
        '''
        self.OutReg = self.ac
        self.__outputs.append(self.OutReg)
        if self.__debug_text:
            print('OUTPUT:')
            self.__print_rtl('OutReg','AC',self.ac)
            print(f'\tPush OutReg to outputs ({self.OutReg:03X})')

    
    def __jump(self):
        '''
        
        '''
        self.pc = self.mar
        if self.__debug_text:
            print('JUMP:')
            print(f'\tPC \u2190 MAR ({self.pc:03X})')
    
    def __skipcond(self):
        if self.mar == 0x000:
            if self.ac < 0:
                self.pc += 1
        elif self.mar == 0x400:
            if self.ac == 0:
                self.pc += 1
        elif self.mar == 0x800:
            if self.ac > 0:
                self.pc += 1
        if self.__debug_text:
            print('SKIPCOND:')
            print(f'\tCondition: 0x{self.mar:03X}')
            print(f'\tPC: 0x{self.pc:03X}')
    
    def __jns(self):
        self.memory.store(self.pc + 1, self.mar)
        self.pc = self.mar + 1
        if self.__debug_text:
            print('JNS:')
            print(f'\tM[MAR] \u2190 PC + 1 ({self.memory.load(self.mar):03X})')
            print(f'\tPC \u2190 MAR + 1 ({self.pc:03X})')
    
    def __jumpi(self):
        self.pc = self.memory.load(self.mar)
        if self.__debug_text:
            print('JUMPI:')
            print(f'\tPC \u2190 M[MAR] ({self.pc:03X})')
    
    def __halt(self):
        self.__exit = True
        if self.__debug_text:
            print('Program Halted')
    
    def __clearTerm(self):
        '''
        Utility function used to clear the terminal
        '''
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def __verify_program_memory(self) -> bool:
        '''
        Verifies there is a program loaded into memory and returns True if the memory is not empty, otherwise returns False and prints a message in the
        terminal.
        '''
        if self.memory.is_empty():
            print('There is no program present in memory')
            return False
        return True

    def execute(self):
        '''
        Executes the program loaded into memory and displays any outputs into the terminal. If there is no assembled program in memory, exits execution.
        '''
        if not self.__verify_program_memory():
            return
        self.__debug_text = False
        self.__exit = False
        self.__initialize()
        self.__clearTerm()
        try:
            while not self.__exit:
                self.__fetch()
                self.__decode()
        except Exception as e:
            print(f'{e}')
        self.__clearTerm()
        self.__display_output()
    
    def execute_stepwise(self):
        '''
        Executes the program loaded into memory in a stepwise manner with detailed MARIE Register Transfer Notation (RTN) and current memory states
        displayed in the terminal. If there is no assembled program in memory, exits execution.
        '''
        if not self.__verify_program_memory():
            return
        self.__debug_text = True
        self.__exit = False
        self.__initialize()
        self.__clearTerm()
        try:
            while not self.__exit:
                self.__fetch()
                self.__decode()
                print(self)
                input('Enter to continue...')
                self.__clearTerm()
        except Exception as e:
            print(f'{e}')
        self.__display_output()
        
class MarieExecutionError(Exception):
    '''
    Marie execution error, triggered where errors arise in program execution
    '''
    def __init__(self, message = 'something went wrong during program execution, check source program.'):
        super().__init__(f'Execution Error: {message}')