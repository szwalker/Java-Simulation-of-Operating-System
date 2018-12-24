'''

Description:
    * This is part of the Banker's algorithm project of operating system simulation.
    * This program simulates FIFO optimistic resource manager.
    * Deadlock detection mechanism has been implemented.
    * Please follow instructions from README.txt to run the program.

Author: Jiaqi Liu

'''

# this is a data structure to represent a task
class Task:
    def __init__(self):
        self.status = 'normal'
        self.remaining_compute_cycle = 0
        self.request_status = 'completed/no request'
        self.total_time_taken = 0
        self.total_waiting_time = 0
        self.resource = [None]
        self.initial_claim = {}
        self.instruction = []
        self.checked = False
        self.pending_request = None
        self.ind = None

    # load instruction to the task's instruction field
    def load_instruction(self,ins):
        self.instruction.append(ins)
        if self.ind == None:
            self.ind = ins[1]

    #  load initial resources that matches the number of resource type
    def load_initial_resources(self,resource_num):
        for i in range(resource_num):
            self.resource.append(0)
    # extract the latest instruction
    def cur_instruction(self):
        if self.status != 'aborted' and self.status!='terminated':
            return self.instruction.pop(0)
        print('err occured in process_instruction method')

    # update task status to new status
    def update_status(self,new_status,compute_cycles=None):
        self.status = new_status
        if compute_cycles!=None and self.status=='compute':
            self.remaining_compute_cycle = compute_cycles

    # return task status
    def get_status(self): return self.status

    # update waiting time and total time of task
    def update_time(self):
        if self.status == 'compute':
            self.total_time_taken += 1
            self.remaining_compute_cycle -= 1
            if self.remaining_compute_cycle == 0:
                self.update_status('normal')

        elif self.status == 'normal':
            self.total_time_taken += 1

        elif self.status == 'request':
            self.total_waiting_time += 1
            self.total_time_taken += 1

    # implement the comparison between tasks based on waiting order
    def __lt__(self,other):
        if self.total_time_taken-self.total_waiting_time == other.total_time_taken-other.total_waiting_time:
            return self.ind < other.ind
        else:
            return self.total_time_taken-self.total_waiting_time < other.total_time_taken-other.total_waiting_time

# round to nearest integer
def my_round(num):
    if num - int(num) >= 0.5:return int(num+1)
    else: return int(num)


def main(filename):
    file = open(filename,'r')
    # extracting task and resource info from the first line of file
    arr = file.readline().rstrip().split(' ')
    task_num = int(arr[0])
    resource_num = int(arr[1])
    # construct a lst of banker's resource
    resource_lst = [None]
    for i in range(2,len(arr)):
        resource_lst.append(int(arr[i]))
    # construct a lst of task objects
    task_lst = [None]
    for j in range(1, task_num+1):
        task = Task()
        task.load_initial_resources(resource_num)
        task_lst.append(task)
    for line in file.readlines():
        # append current instruction to corresponding task object
        ins = line.rstrip().split()
        if len(ins)==0: continue # in case if the line is empty
        ins[1] = int(ins[1])
        ins[2] = int(ins[2])
        ins[3] = int(ins[3])
        task_lst[int(ins[1])].load_instruction(ins)
    # initial set up complete
    ended_tasks = 0
    blocked_count = 0

    # keep running as long as there are task not ended
    while ended_tasks != task_num:

        waiting_q = []
        resource_returned = [None]
        for _ in range(resource_num): resource_returned.append(0)

        # first check blocked (pending) tasks, when done, mark them as checked
        for b in range(1,len(task_lst)):
            cur_task = task_lst[b]
            # blocked tasks has priority to be checked first
            if cur_task.get_status() == 'request' and cur_task.request_status == 'blocked':
                cur_task.checked = True
                waiting_q.append(cur_task)

        # sort waiting tasks in a FIFO order based on the start time of blocked state
        waiting_q.sort()
        for cur_task in waiting_q:
            resource_type,req_amount = cur_task.pending_request
            # have enough resources
            if resource_lst[resource_type] >= req_amount:
                cur_task.resource[resource_type] += req_amount
                resource_lst[resource_type] -= req_amount
                cur_task.update_status('normal')
                cur_task.request_status = 'completed/no request'
                cur_task.update_time()
                blocked_count -= 1

            # do not have enough resources, still blocked
            else:
                cur_task.update_time()


        for i in range(1,len(task_lst)):
            cur_task = task_lst[i]

            if cur_task.get_status() != 'aborted' and cur_task.get_status()!='terminated' and not cur_task.checked:

                if cur_task.get_status()=='compute':
                    cur_task.update_time()
                else:
                    # extract current instruction for current task
                    ins = cur_task.cur_instruction()

                    # initialization process
                    if ins[0] == 'initiate':
                        resource_type = ins[2]
                        claiming_amount = ins[3]
                        cur_task.initial_claim[resource_type] = claiming_amount
                        cur_task.update_status('normal')
                        cur_task.update_time()

                    # process termination
                    elif ins[0] == 'terminate':
                        cur_task.update_status('terminated')
                        ended_tasks += 1
                        # dump all resources into resource collector
                        for j in range(1,len(cur_task.resource)):
                            resource_returned[j] += cur_task.resource[j]
                            cur_task.resource[j] = 0

                    # release resource
                    elif ins[0] == 'release':
                        # release specific resource type into corresponding bucket in resource collector
                        cur_task.update_status('normal')
                        # perform transaction to bank
                        resource_returned[ins[2]]+=ins[3]
                        cur_task.resource[ins[2]]-=ins[3]
                        cur_task.update_time()

                    # perform compute action
                    elif ins[0] == 'compute':
                        cur_task.update_status('compute',ins[2])
                        cur_task.update_time()

                    # current task is requesting resource
                    elif ins[0] == 'request':
                        resource_type = ins[2]
                        req_amount = ins[3]
                        cur_task.update_status('request')
                        # banker has enough resources
                        if resource_lst[resource_type] >= req_amount:
                            cur_task.resource[resource_type]+=req_amount
                            resource_lst[resource_type] -= req_amount
                            cur_task.update_status('normal')
                            cur_task.update_time()
                        # banker does not have enough resource
                        else:
                            cur_task.request_status = 'blocked'
                            cur_task.pending_request = (resource_type,req_amount)
                            blocked_count += 1
                            # pending_queue.insert(0,i)
                            cur_task.update_time()


        # turn off checked bits
        for _ in range(1,len(task_lst)):
            task_lst[_].checked = False


        # deadlock detected
        if blocked_count == task_num-ended_tasks and task_num-ended_tasks!=0:
            print('Deadlock detected!')
            remove_flag = False # flag set to True when tasks is aborted
            pseudo_bank = resource_lst[:]
            # for i in range(len(pending_queue)-1,-1,-1):
            for i in range(1,len(task_lst)):
                # cur_task = task_lst[pending_queue[i]]
                cur_task = task_lst[i]
                resource_type,req_amount = cur_task.pending_request
                # abort the current task
                if cur_task.status == 'request' and cur_task.request_status=='blocked' and req_amount > pseudo_bank[resource_type]:
                    cur_task.update_status('aborted')
                    if remove_flag:
                        print('Deadlock remains after last task removal.')
                    print('Banker aborted task:',cur_task.ind)
                    ended_tasks += 1
                    blocked_count -= 1
                    for r in range(1,len(cur_task.resource)):
                        resource_returned[r] += cur_task.resource[r]
                        pseudo_bank[r] += cur_task.resource[r]
                elif cur_task.status == 'terminated':
                    continue
                # deadlock cycle has been removed
                else:
                    print('Deadlock has been removed.')
                    break


        # move all resource from resource collector to bank
        for k in range(1,len(resource_lst)):
            # print(resource_returned[k])
            resource_lst[k] += resource_returned[k]


    # optimistic resource manager output
    print('\t\tFIFO\t\t')
    # total time for output
    t_time_for_output = 0
    # total wait time for output
    t_wait_for_output = 0
    for t in range(1,len(task_lst)):
        if task_lst[t].status == 'aborted':
            print('Task '+ str(t),'aborted',sep='\t')
        else:
            total_time_taken = task_lst[t].total_time_taken
            total_waiting_time = task_lst[t].total_waiting_time
            t_time_for_output += total_time_taken
            t_wait_for_output += total_waiting_time
            percentage = str(my_round(total_waiting_time/total_time_taken * 100)) + '%'
            print('Task '+ str(t),total_time_taken,total_waiting_time,percentage,sep='\t')
    # total percentage for output
    t_percent_for_output = 'NaN' if t_time_for_output==0 else str(my_round(t_wait_for_output/t_time_for_output * 100))+'%'
    print('total',t_time_for_output,t_wait_for_output,t_percent_for_output,sep='\t')