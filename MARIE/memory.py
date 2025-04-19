# Marie Memory simulation, must contain 4096 bytes of memory.
#
# Author: Steven Short
# Professor: Abdulbast Abushgra
# Date: 4/4/2025
from .abstraction import MemoryABC

class Memory(MemoryABC):
    '''
    Simulated memory with 4096 bytes of space (max storage value 0xFFFF).
    '''
    def __init__(self):
        '''Initializes memory array of size 4096'''
        self.memory = [0x0] * 4096
        self._head = 0 #program head marker
    
    def __str__(self):
        width = 9
        string: str = ''.ljust(width - 1) + '|'

        #Create top row with column labels
        for i in range(0, 16):
            string += f'0x{i:X}'.ljust(width)
        string += '\n'

        # Generate memory matrix up to head value
        row = 0
        clm = 0
        for address in range(0, self._head + 1):
            if clm > 15:
                clm = 0
                row += 0x10
                string += '\n'
            if clm == 0:
                string += f'0x{row:03X}'.ljust(width-1) + '|'
            string += f'0x{self.memory[address]:04X}'.ljust(width)
            clm += 1
        
        #Fill in unfinished row with 0s
        while clm <= 15:
            string += f'0x{0:04X}'.ljust(width)
            clm += 1

        return string
    
    # def __setattr__(self, key, value):
    #     self.store(value, key)
    
    # def __getattribute__(self, key):
    #     return self.load(key)

    def __checkAddressBounds(self, address:int):
        '''
        Utility method used to verify address bounds

        Raises:
            MemoryError: if passed address is outside memory range (4096)
        '''
        if address >= 4096:
            raise MemoryError(f'address out of bounds error (0x{address:04X})')

    def store(self, value: int, address: int):
        '''
        Stores a passed integer value at a target address within the memory

        Args:
            value (int): integer value being stored within the target address
            address (int): target memory address to store within
        
        Raises:
            MemoryError: if passed address is outside memory range (4096) or if passed value exceeds maximum storage size (0xFFFF)
        '''
        self.__checkAddressBounds(address)
        if value <= 0xFFFF:
            self.memory[address] = value
        else:
            raise MemoryError(f'storage bound error (max 0xFFFF)')
        
        # Update head value as needed
        if self._head < address:
            self._head = address

    def load(self, address:int) -> int:
        '''
        Returns value stored in memory at a specified address

        Args:
            address (int): target memory address to read
        
        Raises:
            MemoryError: if passed address is outside memory range (4096)
        '''
        self.__checkAddressBounds(address)
        return self.memory[address]
    
    def saveToFile(self, fileName: str, fileDir: str = './'):
        '''
        Saves data stored within the memory as a '.mre' file.

        Args:
            fileName (str): name of memory file, do not include '.mre' extension
            fileDire (str): target output file directory, default same directory ('./')
        '''
        #convert to save format
        string = ''
        for i in range(0, self._head + 1):
            if i == self._head:
                string += f'{self.memory[i]:04X}'
            else:
                string += f'{self.memory[i]:04X}\n'
    
        #Save to target directory
        with open(f'{fileDir}{fileName}.mre', 'w') as file:
            file.write(string)
    
    def loadFromFile(self, fileName: str, fileDir: str = './'):
        '''
        Loads data into the memory from a '.mre' file.

        Args:
            fileName (str): name of memory file, do not include '.mre' extension
            fileDire (str): file location directory, default same directory ('./')
        '''
        self._head = 0
        with open(f'{fileDir}{fileName}.mre','r') as file:
            for line in file:
                read = line.strip()
                self.memory[self._head] = int(read, 16)
                self._head += 1

class MemoryError(Exception):
    def __init__(self, message = 'memory access error'):
        super().__init__(f'Memory Error: {message}')