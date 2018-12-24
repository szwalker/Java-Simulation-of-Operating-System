'''

Description:
    * This is part of the Banker's algorithm project of operating system simulation.
    * This the driver program, and it takes one parameter as input path for filename.
    * It calls fifo_optimistic.py to simulate FIFO optimistic resource manager, and
        calls banker.py to simulate Banker's algorithm.
    * Please follow instructions from README.txt to run the program.

Author: Jiaqi Liu

'''

import sys,banker,fifo_optimistic

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print('Usage: python3 driver.py <input-file-path>')
        exit(-1)
    filename = sys.argv[1]
    fifo_optimistic.main(filename)
    print('==============================')
    banker.main(filename)
