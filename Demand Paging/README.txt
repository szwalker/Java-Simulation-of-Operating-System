Demand Paging Project

Please follow the instructions below to compile and to execute this program.

1. Open a terminal. Use cd command to get to the present working directory that
contains this README.txt, all the inputs files, as well as all the simulation
programs.

2. Execute the program with specified input parameters.

Please specify the following variables as commandline arguments:
  * M - machine size in words
  * P - the page size in words
  * S - the size of each process
  * J - the type of job mix
  * N - the number of references for each process
  * R - the replacement algorithm: lru, random, or fifo
  * V - verbose option: 0 for regular, 1 for verbose, 11 for show random and verbose

  Sample usage: python3 paging.py M P S J N R V

  Example: paging.py 800 40 400 4 5000 lru 0

Thank you for reading the above information.
