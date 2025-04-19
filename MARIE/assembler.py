# Assembler for Marie assembly code. Acts as a glorified interpreter
# and converts Marie files into a runnable format.
#
# Author: Steven Short
# Professor: Abdulbast Abushgra
# Date: 4/4/2025
from .memory import Memory
from .abstraction import instruction_set, keyWords

class Assembler:
    
    def __init__(self):
        '''
        Marie assembler
        '''
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
            read = line.strip().upper().replace(' ', '')
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

            # Raise error if line cotains multiple address markers
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


    def assembleFile(self, filepath: str) -> bool:
        '''
        Attempts to assemble Marie assembly code from a target filepath. Returns True if the Assembly was successful. The assembled programs
        are inserted into a MemoryABC object in a MARIE readable format.

        Args:
            filepath (str): target file path to assemble
        
        Returns:
            complete (bool): True if the assembly was successful, otherwise False
        '''
        self._itr = 0
        self._readOffset = 0
        complete = False
        with open(filepath, 'r') as file:
            try:
                #Scan document for errors
                for line in self.__nonBlank(file):
                    self.__scan(line)
                    self._itr += 1
                
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