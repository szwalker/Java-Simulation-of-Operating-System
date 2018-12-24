'''

Description:
    * This is part of the Banker's algorithm project of operating system simulation.
    * This program simulates Banker's algorithm.
    * State detection mechanism has been implemented so banker will never enter unsafe state.
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

# mini task, simplified version of a task structure
class mini_task:
    def __init__(self,ct):
        self.total_have = ct.resource[:]
        self.total_need = [None]
        self.status = 'live' if ct.get_status()!='aborted' and ct.get_status()!='terminated' else 'dead'
        for i in range(1,len(self.total_have)):
            need = ct.initial_claim[i] - self.total_have[i]
            self.total_need.append(need)


# round to nearest integer
def my_round(num):
    if num - int(num) >= 0.5:return int(num+1)
    else: return int(num)

# safe state determination
def is_safe_state(task_lst,resource_lst,ins):
    fake_task_lst = [None]
    live_task_count = 0
    # construct a fake task list to simply the relationship between tasks and avoid direct operating on original tasks
    for i in range(1,len(task_lst)):
        ct = task_lst[i]
        if ct.get_status() != 'aborted' and ct.get_status() != 'terminated':
            live_task_count += 1
        # convert current task into a mini task (simplified version of original task) to perform safety check
        cur_mini_task = mini_task(ct)
        fake_task_lst.append(cur_mini_task)

    fake_resource_lst = resource_lst[:]


    # pretend banker grant the requested resource to current task
    fake_task_lst[ins[1]].total_have[ins[2]] += ins[3]
    fake_task_lst[ins[1]].total_need[ins[2]] -= ins[3]
    fake_resource_lst[ins[2]] -= ins[3]

    # check: can banker finish any more task now?

    while True:
        orig = live_task_count
        for j in range(1,len(fake_task_lst)):
            cur_mini_task = fake_task_lst[j]
            can_terminate_flag = True
            for r in range(1,len(cur_mini_task.total_need)):
                if cur_mini_task.total_need[r] > fake_resource_lst[r]:
                    can_terminate_flag = False
            if can_terminate_flag:
                for r in range(1,len(cur_mini_task.total_have)):
                    fake_resource_lst[r] += cur_mini_task.total_have[r]
                    cur_mini_task.total_have[r] = 0
                    cur_mini_task.total_need[r] = 0
                cur_mini_task.status = 'dead'
                live_task_count -= 1
        # Banker cannot terminate at least one task - unsafe state
        if live_task_count == orig and live_task_count!=0:
            return False
        # safe state, all tasks can be killed.
        elif live_task_count<= 0:
            return True



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
    banker_origin = resource_lst[:] # test
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
            ins = cur_task.pending_request
            # banker's safe state checking
            if is_safe_state(task_lst,resource_lst,ins):
                resource_type = ins[2]
                req_amount = ins[3]
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
                        if claiming_amount > banker_origin[resource_type]:
                            print('Task ',cur_task.ind,"'s initial claim on resource type ",resource_type," exceeds of units present!",sep='')
                            cur_task.update_status('aborted')
                            ended_tasks += 1
                            # dump its resource to resource collector
                            for r in range(1,len(cur_task.resource)):
                                resource_returned[r] += cur_task.resource[r]
                        else:
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
                        # check whether the request exceeded its initial claim
                        if req_amount + cur_task.resource[resource_type] > cur_task.initial_claim[resource_type]:
                            print('Task ',cur_task.ind,"'s request request exceeds its claim - aborted!",sep='')
                            cur_task.update_status('aborted')
                            ended_tasks += 1
                            # dump its resource to resource collector
                            for r in range(1,len(cur_task.resource)):
                                resource_returned[r] += cur_task.resource[r]

                        # banker believes this is a safe state
                        elif is_safe_state(task_lst,resource_lst,ins):
                            cur_task.resource[resource_type]+=req_amount
                            resource_lst[resource_type] -= req_amount
                            cur_task.update_status('normal')
                            cur_task.update_time()

                        # banker determines this is an unsafe state
                        else:
                            cur_task.request_status = 'blocked'
                            cur_task.pending_request = ins
                            blocked_count += 1
                            cur_task.update_time()

        # turn off checked bits
        for _ in range(1,len(task_lst)):
            task_lst[_].checked = False

        # move all resource from resource collector to bank
        for k in range(1,len(resource_lst)):
            resource_lst[k] += resource_returned[k]


    # optimistic resource manager output
    print("\t\tBANKER'S\t\t")
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