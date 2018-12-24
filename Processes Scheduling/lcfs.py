'''

Description:
    * This is part of the project of operating system scheduling simulation.
    * This program simulates Last Come First Serve.
    * Tie-breaking mechanism is designed in this program to handle processes with
        same priorities become ready at the same time.
    * Please follow instructions from README.txt to run the program.

Author: Jiaqi Liu

'''

from ArrayStack import ArrayStack
import sys

class Job:
    def __init__(self,A,B,C,M,ind):
        self.A = A # arrival time
        self.B = B # CPU burst range
        self.C = C # CPU time needed
        self.M = M # multiplier
        self.ind =ind # index in input list - for tie break
        self.state = 'unstarted'
        self.cpu_burst_remaining = 0
        self.blocked_remaining = 0
        self.total_cpu_time = 0
        self.total_blocking_time = 0
        self.total_waiting_time = 0
        self.finishing_time = None
        self.first_ready_time = None

    def get_waiting_time(self):
        return self.total_waiting_time

    def get_turn_around_time(self):
        return self.finishing_time - self.first_ready_time

    def increment_waiting_time(self):
        self.total_waiting_time += 1

    def __lt__(self,other):
        if self.A < other.A:
            return True
        elif self.A == other.A:
            return self.ind < other.ind
        else:
            return False

    def status_check(self,time):
        global cpu_can_run,job_incomplete
        if self.state == 'unstarted' and time >= self.A:
            self.first_ready_time = time
            self.state = 'ready'
        elif self.state == 'blocked' and self.blocked_remaining == 0:
            self.state = 'ready'
        elif self.state == 'running' and self.total_cpu_time == self.C:
            self.state = 'terminated'
            self.finishing_time = time
            job_incomplete-=1 # reduce incomplete job count
            cpu_can_run = True
        elif self.state == 'running' and self.cpu_burst_remaining == 0:
            self.state = 'blocked'
            cpu_can_run = True

    def status_report(self):
        # the cpu and blocked remaining status comes with 1 round delay
        if self.state == 'running':
            return self.state + ' ' + str(self.cpu_burst_remaining+1)
        elif self.state == 'blocked':
            return self.state + ' ' + str(self.blocked_remaining+1)
        else:
            return self.state + ' ' + str(0)

    def is_ready(self):
        return self.state == 'ready'

    def start_run(self):
        global cpu_can_run
        cpu_can_run = False
        self.state = 'running'
        self.cpu_burst_remaining = randomOS(self.B)
        # in case if the cpu burst is greater than the time needed to complete job
        # if self.total_cpu_time + self.cpu_burst_remaining > self.C:
            # then switch to the number just necessary to complete job
            # self.cpu_burst_remaining = self.C - self.total_cpu_time
        # blocking time is the cpu burst times multiplier
        self.blocked_remaining = self.cpu_burst_remaining * self.M

    def run_controller(self):
        global cpu_can_run
        self.cpu_burst_remaining -= 1
        self.total_cpu_time += 1

    def block_controller(self):
        self.blocked_remaining -= 1
        self.total_blocking_time += 1

    def get_state(self):
        return self.state

    def __str__(self):
        return ' '.join([str(self.A),str(self.B),str(self.C),str(self.M)])

    def final_report(self,process_num):
        res = 'Process %1d\n\t'%(process_num)
        res += '(A,B,C,M) = (%s)\n\t' %(','.join([str(self.A),str(self.B),str(self.C),str(self.M)]))
        res += 'Finishing time: %3d\n\t' %(self.finishing_time)
        res += "Turnaround time: %2d\n\t" %(self.finishing_time-self.first_ready_time)
        res += 'I/O time: %3d\n\t' %(self.total_blocking_time)
        res += 'Waiting time: %3d\n' %(self.total_waiting_time)
        print(res)

# generate a random CPU burst time based on CPU burst limit
def randomOS(U):
    global random_num_ind
    num = 1+ random_num_lst[random_num_ind] % U
    random_num_ind += 1
    return num

def loadRamdomNum():
    f = open('random-numbers.txt')
    lines_lst = f.readlines()
    res = []
    for line in lines_lst:
        line.rstrip()
        res.append(int(line))
    f.close()
    return res

# return a list of cleaned jobs
def read_jobs(filepath):
    step = 4
    f = open(filepath,'r')
    lines_lst = f.readlines()
    res = []
    index = 0
    cur_job_num = None
    for line in lines_lst:
        line = line.rstrip()
        print("The original input was:",line)
        line = line.split(' ')
        cur_job_num = int(line[0])
        for i in range(1, step*cur_job_num,step):
            A = int(line[i])
            B = int(line[i+1])
            C = int(line[i+2])
            M = int(line[i+3])
            res.append(Job(A,B,C,M,index))
            index+=1
    f.close()
    res.sort()
    sorted_output = 'The (sorted) input is: %1d ' %(cur_job_num)
    for j in res:
        sorted_output += str(j) + ' '
    print(sorted_output)
    return res


# require each process perform a status check
# filter the ready jobs and add to Q following tie-break rules
def scan_job(Q,lst,time):
    join_queue = []
    for j in lst:
        j.status_check(time)
        if j.is_ready():
            join_queue.append(j)
    join_queue.sort() # tie-break mechanism
    join_queue.reverse() # 反转然后压进stack
    for i in join_queue:
        if i not in Q:
            Q.push(i)

def cycle_report(cycle,jobs_lst):
    report = 'Before cycle %4s :' %(str(cycle))
    for i in jobs_lst:
        report += ' %13s' %(i.status_report())
    report += '.'
    print(report)

if __name__ == "__main__":
    if (len(sys.argv)<2):
        print("Please follow one of the following usage:")
        print("usage: python3 <program-name> <input-filename>")
        print("usage: python3 <program-name> --verbose <input-filename>")
        exit(-1)

    detailed_mode = False
    filepath = None

    if (len(sys.argv)==3):
        if sys.argv[1] == '--verbose':
            detailed_mode = True
        filepath = sys.argv[2]

    elif (len(sys.argv)==2):
        filepath = sys.argv[1]

    unsorted_jobs_lst = []
    random_num_ind = 0
    random_num_lst = loadRamdomNum()
    jobs_lst = read_jobs(filepath)
    S = ArrayStack()
    cpu_can_run = True
    job_incomplete = len(jobs_lst)
    time = 0
    run_lst = []
    block_lst = []
    job_is_running_time = 0 # to calc cpu utilization
    job_is_blocking_time = 0 # to calc i/o utilization
    if detailed_mode:
        print("\nThis detailed printout gives the state and remaining burst for each process.\n")
    while job_incomplete > 0:
        # one time unit is one cycle
        if detailed_mode:
            cycle_report(time,jobs_lst)
        # scan status for change
        scan_job(S,jobs_lst,time)

        if not S.is_empty() and cpu_can_run:
            cur_job = S.pop()
            cur_job.start_run()

        job_running_in_cur_cycle = False
        job_is_blocking_in_cur_cycle = False
        for j in jobs_lst:
            if j.get_state() == 'running':
                j.run_controller()
                job_running_in_cur_cycle = True
            elif j.get_state() == 'blocked':
                j.block_controller()
                job_is_blocking_in_cur_cycle = True
            elif j.get_state() == 'ready':
                j.increment_waiting_time()

        if job_running_in_cur_cycle:
            job_is_running_time += 1
        if job_is_blocking_in_cur_cycle:
            job_is_blocking_time += 1

        time +=1

    print("The scheduling algorithm used was Last Come First Served\n")

    total_waiting_time = 0
    total_turnaround_time = 0
    total_jobs = len(jobs_lst)
    total_cpu_util = 0

    # report final information for each process
    for i,j in enumerate(jobs_lst):
        j.final_report(i)
        total_waiting_time += j.get_waiting_time()
        total_turnaround_time += j.get_turn_around_time()
        total_cpu_util += j.total_cpu_time / j.finishing_time

    batch_finishing_time = time - 1
    avg_waiting_time = total_waiting_time / total_jobs
    avg_turnaround_time = total_turnaround_time / total_jobs

    summary_data = 'Summary Data:\n\tFinishing time: %4d\n\t'%batch_finishing_time
    summary_data+= 'CPU Utilization: %s\n\t' %format(job_is_running_time/batch_finishing_time,'.6f')
    summary_data+= 'I/O Utilization: %s\n\t' %format(job_is_blocking_time/batch_finishing_time,'.6f')
    summary_data+= 'Throughput: %s processes per hundred cycles\n\t' %format(total_jobs * 100/batch_finishing_time,'.6f')
    summary_data+= 'Average turnaround time: %1.6f\n\t' %avg_turnaround_time
    summary_data+= 'Average waiting time: %1.6f\n\t' %avg_waiting_time
    print(summary_data)