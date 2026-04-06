# Assembler for Marie assembly code. Acts as a glorified interpreter
# and converts Marie files into a runnable format.
#
# Author: Steven Short
# Professor: Abdulbast Abushgra
# Date: 4/4/2025
# Revised: 2/26/2026
from pathlib import Path
import re
from .memory import Memory

# TODO: Add STOREI and LOADI Support

#Marie instruction set
instruction_set = {
            'ADD': 0x3,
            'SUBT': 0x4,
            'ADDI': 0xB,
            'CLEAR': 0xA,
            'LOAD': 0x1,
            'STORE': 0x2,
            'INPUT': 0x5,
            'OUTPUT': 0x6,
            'JUMP': 0x9,
            'SKIPCOND': 0x8,
            'JNS': 0x0,
            'JUMPI': 0xC,
            'HALT': 0x7
        }

# Language keywords
keyWords = ['HEX','DEC', 'ADD', 'SUBT', 'ADDI', 'CLEAR', 'LOAD', 'STORE', 'INPUT', 'OUTPUT', 'JUMP', 'SKIPCOND', 'JNS', 'JUMPI', 'HALT']

class Assembler:
    '''
        Marie assembler responsible for interpreting and loading MARIE programs into simulated memory.

        Independently generates a Memory object and interprets a passed Marie assembly file into that memory object.
        This simulates a low-level programs assembly for CPU execution.

        Examples:
    '''
    def __init__(self):
        
        self.memory = Memory()
        self.address_book = {} # keeps track of specified addresses
        self.instruction_set = instruction_set
        self._itr = 0
        self._readOffset = 0
    
    def __getOperatingLine(self) -> str:
        return f'{self._itr + 1 + self._readOffset}'
        
    def __nonBlank(self, file):
        '''
        Generator function used to return non-blank lines within a read file
        '''
        for line in file:
            read = line.strip().upper()
            read = read[:read.find('/')] if '/' in read else read
            if read:
                yield read
            else:
                self._readOffset += 1
    
    def __readComponents(self, file):
        '''
        Generator function used to iterate a passed file and yield component lists formatted for MARIE command interpretation.
        '''
        for line in file:
            read = line.strip().upper()
            read = re.sub(r'[ \t]+','',read) #cleans line of spaces and tabs should they exist
            read = read[:read.find('/')] if '/' in read else read
            if read:
                read = read.split(',')[1] if ',' in read else read
                
                #Read line left to right
                out = []
                r = ''
                while read:
                    r += read[0]
                    read = read[1:]

                    if r in keyWords:
                        out.append(r)
                        r = ''
                #Last component expected to be operand
                if r:
                    out.append(r)
                yield out
            else:
                self._readOffset += 1

    def __scan(self, line:str):
        '''
        Initial document scan function focused on building an address book for use during line interpretation and detecting keyword errors.

        Args:
            line (str): Document line being scanned
        
        Raises:
            MarieAssemblyError: if addressig or keyword errors exist
        '''
        ln = line

        #Build address book and check for addressing errors
        if ',' in ln:
            tmp = ln.split(',')

            # Raise error if line contains multiple address markers
            if (len(tmp) > 2):
                raise MarieAssemblyError(f'addressing error at line {self.__getOperatingLine()}')
            if not tmp[0]:
                raise MarieAssemblyError(f'missing address label at line {self.__getOperatingLine()}')
            ad = tmp[0]
            ln = tmp[1]
            self.address_book[ad] = self._itr
        
        # Ensure every line contains a keyword
        if not any(kw in line for kw in keyWords):
            raise MarieAssemblyError(f'keyword missing exception at line {self.__getOperatingLine()}')
    
    def __interpret(self, components:list) -> int:
        '''
        Interprets pre-prossessed lists containing MARIE keywords, integers, and address values. The __readComponents()
        generator method is used to create these component lists.

        Args:
            component (list): List containing MARIE keywords, integers, and addresses
        
        Returns:
            16-bit integer value containing MARIE style opcode and operand (0xFFFF)
        '''
        isInt, isHex = False, False
        opcode = 0x0
        operand = 0x0
        for cmp in components:
            if isInt:
                try:
                    if isHex:
                        operand = int(cmp,16)
                        isHex = False
                    else:
                        operand = int(cmp)
                    isInt = False
                except:
                    raise MarieAssemblyError(f'integer expected at line {self.__getOperatingLine()}')
            else:
                if cmp in keyWords:
                    if cmp in ['HEX','DEC']:
                        isInt = True
                        if cmp == 'HEX':
                            isHex = True
                        continue
                    opcode = self.instruction_set[cmp]
                    continue
                operand = self.address_book[cmp] if cmp in self.address_book else self.__checkSkipcond(cmp)
        return opcode << 12 | operand
    
    def __checkSkipcond(self, string: str) -> int:
        '''
        Helper function used to verify skipcond operands. Accepts a string value and attempts to interpret the value as a hexadecimal integer.

        Args:
            string (str): string expected to contain the scipcond opperand
        
        Returns:
            MARIE style SkipCond condition value [0x000, 0x400, 0x800]
        
        Raises:
            MarieAssemblyError: If there is a ValueError thrown during conversion or if operand is outside the accepted skipcond operand inputs [000, 400, 800]
        '''
        try:
            value = int(string, 16)
        except:
            raise MarieAssemblyError(f'value error at line {self.__getOperatingLine()}')
        if value in [0x000, 0x400, 0x800]:
            return value
        else:
            raise MarieAssemblyError(f'skipcond improper condition passed at line {self.__getOperatingLine()}')

    def __find_file_path(self, directory:str, filename:str) -> Path | None:
        '''
        Finds and returns the path to a target file within the specified directory as a Path object, otherwise returns None.


        '''
        directory_path = Path(directory)

        for file in directory_path.rglob(filename):
            return file
        
        return None

    def assembleFile(self, filename: str, directory:str = '.') -> bool:
        '''
        Attempts to assemble Marie assembly code from a target file. Returns True if the Assembly was successful. The assembled programs
        are inserted into a Memory object in a MARIE readable format.

        Args:
            filepath (str): target file path to assemble
        
        Returns:
            complete (bool): True if the assembly was successful, otherwise False
        '''
        self._itr = 0
        self._readOffset = 0
        complete = False

        file_path = self.__find_file_path(directory, filename)
        if file_path:
            with file_path.open('r') as file:
                try:
                    #Scan document for errors
                    for line in self.__nonBlank(file):
                        self.__scan(line)
                        self._itr += 1
                    
                    print(self.address_book)
                    
                    #Interpret document
                    file.seek(0)
                    self._itr = 0
                    self._readOffset = 0
                    for cmp in self.__readComponents(file):
                        value = self.__interpret(cmp)
                        self.memory.store(value,self._itr)
                        self._itr += 1
                    complete = True

                except Exception as e:
                    print(f'{e}')
        return complete

class MarieAssemblyError(Exception):
    '''
    Marie program assembly exception thrown during assembly errors
    '''
    def __init__(self, message = 'file could not be assembled as passed.'):
        super().__init__(f'Assembly Error: {message}')