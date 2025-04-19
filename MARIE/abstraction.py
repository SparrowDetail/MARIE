# Abstract definition for the MARIE simple computer. Outlines
# expected functionality and provides base datatype.
# Includes Memory abstraction
#
# Author: Steven Short
# Professor: Abdulbast Abushgra
# Date: 3/21/2025

from abc import ABC, abstractmethod

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

class MemoryABC(ABC):
    '''
    Abstract definition of the memory simulator. Provides interfaces for querying and storing values within a Marie
    like system. Should contain 4096 bytes of memory (simulated with an array of size 4096).
    '''
    def store(self, value:int, address:int):
        '''
        Store a passed value at the target address.

        Args:
            value (int): hex/decimal value to store
            address (int): hex/decimal value for the target address
        '''
        pass

    def load(self, address:int) -> int:
        '''
            Load and return the value at a passed address, default return 0x0.

            Args:
                address (int): hex/decimal value for the target address
        '''
        pass