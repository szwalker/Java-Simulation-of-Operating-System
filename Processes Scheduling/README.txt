CSCI-UA 202 Operating System

Scheduler Project

Author: Jiaqi Liu

Netid: jl8456

Please note: This program assumes there are ***no parameters*** between processes
from input text file that simulates processes.

Please follow the instructions below to compile and to execute this program.

1. Open a terminal. Use cd command to get to the present working directory that
contains this README.txt, all the inputs files, as well as all the simulation
programs.

The project simulates four types of scheduler. Types of scheduler and
corresponding program names are as follows:

  Type of Scheduler                           Program Name
  First Come First Serve                        fcfs.py
  Round Robin with quantum 2                    rr.py
  Last Come First Serve                         lcfs.py
  High Penalty Ratio Next                       hprn.py

2. Execute the program with specified input file.

You may use "--verbose" command if you want to see the detailed version,
which prints out the state and remaining burst for each process.

To see brief version (simulation summary only), enter:
python3 <program-name> <input-filename>

To see detailed simulation version, enter:
usage: python3 <program-name> --verbose <input-filename>

Example:
python3 rr.py --verbose input-4.txt

This command will print out a detailed version of simulation processes
specified from input-4.txt using Round Robin with quantum 2 scheduler.


Thank you for reading the above information.
