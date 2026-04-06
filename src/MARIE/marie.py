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
    
    def __printRegisterAction(self, register1:str, register2:str, value:str):
        '''
        MARIE helper method used to print register actions in MARIE Register Transfer Language (RTL) format (MAR → PC (0x003)).
        This method will include the value being passed in parenthesis next to the the RTL text.

        Args:
            register1 (str): First register in RTL format (value copied from).
            register2 (str): Second register in RTL format (value copied to).
            value (str): Register value being copied as a string
        
        Examples:
            Print register action, MAR value transfered to PC:

            >>>_printRegisterAction("MAR", "PC", "0x003")
            MAR → PC (0x003)
        '''
        print(f'\t{register1} \u2190 {register2} ({value})')

    def __fetch(self):
        '''
        MARIE helper function that controls register actions for the MARIE fetch instruction.
        '''
        self.MAR = self.PC
        self.MBR = self.memory.load(self.MAR)
        self.IR = self.MBR
        self.PC += 1
        if self.__debugText: 
            print('Fetch:')
            self.__printRegisterAction('MAR','PC',f'{self.MAR}')
            self.__printRegisterAction('MBR', 'M[MAR]', f'{self.MBR}')
            self.__printRegisterAction('IR', 'MBR', f'{self.IR}')
            self.__printRegisterAction('PC', 'PC + 1', f'{self.PC}')
    
    def __decode(self):
        '''
        MARIE helper function that interprets the data stored within the Instruction Register (IR) based on MARIE instruction set.

        Raises:
            MarieExecutionError: If stored instruction is outside instruction set.
        '''
        inst = (self.IR >> 12) & 0xF
        self.MAR = self.IR & 0xFFF
        action = self.__control.get(inst)
        if self.__debugText:
            print(f'Decode IR[15-12] (0x{inst:X}):')
            self.__printRegisterAction('MAR','IR[15-12]',f'0x{self.MAR:03X}')
        if action:
            action()
        else:
            raise MarieExecutionError(f'critical error, passed instruction outside instruction set (address {self.PC - 1})')
    
    def __add(self):
        '''
        MARIE helper function that simulates the add instruction (add value at MAR address to AC register).

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
            self.__printRegisterAction('MBR','M[MAR]',f'0x{self.MBR:03X}')
            self.__printRegisterAction('AC','AC + MBR',f'0x{self.AC:03X}')

    def __subt(self):
        '''
        MARIE helper function that simulates the subt instruction (subtract value at MAR address from AC register).

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
            self.__printRegisterAction('MBR','M[MAR]',f'0x{self.MBR:03X}')
            self.__printRegisterAction('AC','AC - MBR',f'0x{self.AC:03X}')

    
    def __addi(self):
        '''
        MARIE helper function that simulates the addi, or add indirect, instruction.
        
        Uses the address stored at the target address to retrieve a value and add that value to the AC register.

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
            print(f'\tMBR \u2190 M[MAR] (0x{self.MAR:03X})')
            print(f'\tMAR \u2190 MBR')
            print(f'\tMBR \u2190 M[MAR] (0x{self.MBR:04X})')
            print(f'\tAC \u2190 AC + MBR (0x{self.AC:03X})')
    
    def __clear(self):
        '''
        Sets the AC register to a zeroed state.
        '''
        self.AC = 0x0
        if self.__debugText:
            print('CLEAR:')
            print(f'\tAC \u2190 0x0')
    
    def __load(self):
        '''
        Loads the value at a the 
        '''
        try:
            self.AC = self.memory.load(self.MAR)
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debugText:
            print('LOAD:')
            print(f'\tAC \u2190 M[MAR] ({self.AC:03X})')
    
    def __store(self):
        try:
            self.memory.store(self.AC , self.MAR)
        except Exception as e:
            raise MarieExecutionError('f{e}')
        if self.__debugText:
            print('STORE:')
            print(f'\tM[MAR] \u2190 AC ({self.AC:03X})')
    
    def __input(self):
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
            print('\tInReg \u2190 Keyboard ')
            print(f'\tAC \u2190 InReg ({self.InReg:03X})')
    
    def __output(self):
        self.OutReg = self.AC
        self.__outputs.append(self.OutReg)
        if self.__debugText:
            print('OUTPUT:')
            print('\tOutReg \u2190 AC')
            print(f'\tPush OutReg to outputs ({self.OutReg:03X})')

    
    def __jump(self):
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
        self.PC = 0x0
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
    Marie execution error, triggered where errors arrise in program execution
    '''
    def __init__(self, message = 'something whent wrong during program execution, check source program.'):
        super().__init__(f'Execution Error: {message}')