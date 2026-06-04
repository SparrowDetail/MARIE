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
    """Marie class that simulates internal architecture of the Marie Simple Computer example"""
    def __init__(self, mem: Memory = Memory()):
        self.AC = 0x0
        self.MAR = 0x0
        self.MBR = 0x0
        self.PC = 0x0
        self.IR = 0x0
        self.InReg = 0x0
        self.OutReg = 0x0
        self.memory = mem
        self.__exit = False
        self.__debugText = False
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
        out += f'AC: {self.AC:04X}'.ljust(width)
        out += f'MAR: {self.MAR:04X}'.ljust(width)
        out += f'MBR: {self.MBR:04X}'.ljust(width)
        out += f'PC: {self.PC:04X}'.ljust(width)
        out += f'IR: {self.IR:04X}'.ljust(width)
        out += f'InReg: {self.InReg:04X}'.ljust(width)
        out += f'OutReg: {self.OutReg:04X}'.ljust(width)

        out += f'\n\n{self.memory}'

        return out

    def __initialize(self):
        '''
        MARIE helper method used to re-initialize MARIE registers to default values.
        '''
        self.AC = 0x0
        self.MAR = 0x0
        self.MBR = 0x0
        self.PC = 0x0
        self.IR = 0x0
        self.InReg = 0x0
        self.OutReg = 0x0
        self.__exit = False
        self.__outputs = []
    
    def __displayOutput(self):
        '''
        MARIE helper method used to display output values as hexadecimal or decimal values as prompted by user input.
        '''
        isHex = True if input('Display output as hexadecimal values (Y/N)?').upper().startswith('Y') else False
        print('\nOutput:')
        for o in self.__outputs:
            if isHex: 
                print(f'\t0x{o:03X}')
            else:
                print(f'\t{o}')
    
    def __printRegisterAction(self, register1:str, register2:str, value:int, fourDigitRegister:bool = False):
        '''
        MARIE helper method used to print register actions in MARIE Register Transfer Language (RTL) format (MAR → PC (0x003)).
        This method will include the value being passed in parenthesis next to the the RTL text.

        Args:
            register1 (str): First register in RTL format (value copied from).
            register2 (str): Second register in RTL format (value copied to).
            value (str): Register value being copied as a string
            fourDigitRegister (bool): Optional boolean display modifier that displays the value as a four digit hex number, otherwise display as a three digit number
        
        Examples:
            Print register actions:

            >>> Marie.__printRegisterAction("MAR", "PC", 3)
                MAR ← PC (0x003)

            >>> Marie.__printRegisterAction("MBR", "M[MAR]", 10, True)
                MBR ← M[MAR] (0x000A)
        '''
        if (fourDigitRegister):
            formatted_value = f'{value:04X}'
        else:
            formatted_value = f'{value:03X}'

        print(f'\t{register1} \u2190 {register2} (0x{formatted_value})')

    def __fetch(self):
        '''
        MARIE helper function that controls register actions for the MARIE fetch instruction. 
        
        If debug text is set to true, will print Register Transfer Language steps to terminal.
        '''
        self.MAR = self.PC
        self.MBR = self.memory.load(self.MAR)
        self.IR = self.MBR
        self.PC += 1
        if self.__debugText: 
            print('Fetch:')
            self.__printRegisterAction('MAR','PC',self.MAR)
            self.__printRegisterAction('MBR', 'M[MAR]', self.MBR, True)
            self.__printRegisterAction('IR', 'MBR', self.IR)
            self.__printRegisterAction('PC', 'PC + 1', self.PC)
    
    def __decode(self):
        '''
        Interprets the data stored within the Instruction Register (IR) based on MARIE instruction set.

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If stored instruction is outside instruction set.
        '''
        inst = (self.IR >> 12) & 0xF
        self.MAR = self.IR & 0xFFF
        action = self.__control.get(inst)
        if self.__debugText:
            print(f'Decode IR[15-12] (0x{inst:X}):')
            self.__printRegisterAction('MAR','IR[15-12]',self.MAR)
        if action:
            action()
        else:
            raise MarieExecutionError(f'critical error, passed instruction outside instruction set (address {self.PC - 1})')
    
    def __add(self):
        '''
        Simulates the addition instruction (add value at MAR address to AC register).

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If target memory block is out of range.
        '''
        try:
            self.MBR = self.memory.load(self.MAR)
            self.AC += self.MBR
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debugText:
            print('ADD:')
            self.__printRegisterAction('MBR','M[MAR]',self.MBR)
            self.__printRegisterAction('AC','AC + MBR',self.AC)

    def __subt(self):
        '''
        Simulates the subtract instruction (subtract value at MAR address from AC register).

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If target memory block is out of range.
        '''
        try:
            self.MBR = self.memory.load(self.MAR)
            self.AC -= self.MBR
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debugText:
            print('SUBT:')
            self.__printRegisterAction('MBR','M[MAR]',self.MBR)
            self.__printRegisterAction('AC','AC - MBR',self.AC)

    
    def __addi(self):
        '''
        Simulates Marie the add indirect instruction. Uses the address stored at the target address to retrieve a value and add that value to the accumulator (AC) register.

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If any address is out of range.
        '''
        try:
            self.MBR = self.memory.load(self.MAR)
            self.MAR = self.MBR
            self.MBR = self.memory.load(self.MAR)
            self.AC += self.MBR
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debugText:
            print('ADDI:')
            self.__printRegisterAction('MBR','M[MAR]',self.MAR,True)
            self.__printRegisterAction('MAR','MBR',self.MAR)
            self.__printRegisterAction('MBR','M[MAR]',self.MBR,True)
            self.__printRegisterAction('AC','AC + MBR',self.AC)
    
    def __clear(self):
        '''
        Sets the AC register to a zeroed state.

        If debug text is set to true, will print Register Transfer Language steps to terminal.
        '''
        self.AC = 0x0
        if self.__debugText:
            print('CLEAR:')
            self.__printRegisterAction('AC','0x0',self.AC)
    
    def __load(self):
        '''
        Loads the value at a the address stored within the MAR register.

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If the target address is outside the maximum address range (4096)
        '''
        try:
            self.AC = self.memory.load(self.MAR)
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debugText:
            print('LOAD:')
            self.__printRegisterAction('AC','M[MAR]',self.AC)
    
    def __store(self):
        '''
        Stores the value of the AC register to the memory address stored within the MAR register

        If debug text is set to true, will print Register Transfer Language steps to terminal.

        Raises:
            MarieExecutionError: If the passed address is outside the maximum address range (4096) or the stored value exceeds the maximum memory size (0xFFFF)
        '''
        try:
            self.memory.store(self.AC , self.MAR)
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debugText:
            print('STORE:')
            print(f'\tM[MAR] \u2190 AC ({self.AC:03X})')
    
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
        self.AC = self.InReg
        if self.__debugText:
            print('INPUT:')
            self.__printRegisterAction('InReg','Keyboard',self.InReg)
            self.__printRegisterAction('AC','InReg',self.AC)
    
    def __output(self):
        '''
        Appends the current value of the accumulator to an internal output array for display at the end of program execution.

        If debug text is set to true, will print Register Transfer Language steps to terminal.
        '''
        self.OutReg = self.AC
        self.__outputs.append(self.OutReg)
        if self.__debugText:
            print('OUTPUT:')
            self.__printRegisterAction('OutReg','AC',self.AC)
            print(f'\tPush OutReg to outputs ({self.OutReg:03X})')

    
    def __jump(self):
        '''
        
        '''
        self.PC = self.MAR
        if self.__debugText:
            print('JUMP:')
            print(f'\tPC \u2190 MAR ({self.PC:03X})')
    
    def __skipcond(self):
        if self.MAR == 0x000:
            if self.AC < 0:
                self.PC += 1
        elif self.MAR == 0x400:
            if self.AC == 0:
                self.PC += 1
        elif self.MAR == 0x800:
            if self.AC > 0:
                self.PC += 1
        if self.__debugText:
            print('SKIPCOND:')
            print(f'\tCondition: 0x{self.MAR:03X}')
            print(f'\tPC: 0x{self.PC:03X}')
    
    def __jns(self):
        self.memory.store(self.PC + 1, self.MAR)
        self.PC = self.MAR + 1
        if self.__debugText:
            print('JNS:')
            print(f'\tM[MAR] \u2190 PC + 1 ({self.memory.load(self.MAR):03X})')
            print(f'\tPC \u2190 MAR + 1 ({self.PC:03X})')
    
    def __jumpi(self):
        self.PC = self.memory.load(self.MAR)
        if self.__debugText:
            print('JUMPI:')
            print(f'\tPC \u2190 M[MAR] ({self.PC:03X})')
    
    def __halt(self):
        self.__exit = True
        if self.__debugText:
            print('Program Halted')
    
    def __clearTerm(self):
        '''
        Utility function used to clear the terminal
        '''
        os.system('cls' if os.name == 'nt' else 'clear')

    def execute(self):
        self.__debugText = False
        self.__initialize()
        self.__clearTerm()
        try:
            while not self.__exit:
                self.__fetch()
                self.__decode()
        except Exception as e:
            print(f'{e}')
        self.__clearTerm()
        self.__displayOutput()
    
    def executeStepwise(self):
        self.__debugText = True
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
        self.__displayOutput()
        
class MarieExecutionError(Exception):
    '''
    Marie execution error, triggered where errors arise in program execution
    '''
    def __init__(self, message = 'something went wrong during program execution, check source program.'):
        super().__init__(f'Execution Error: {message}')