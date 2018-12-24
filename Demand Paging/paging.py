'''

Description:
    * This program simulates Demand Paging in operating system.
    * Please follow instructions from README.txt to run the program.

Author: Jiaqi Liu

'''
import sys
class FrameTable:
    class Frame:
        def __init__(self,frame_num):
            self.frame_num = frame_num
            self.is_occupied = False
            self.occupied_process = None
            self.word_range = None
            self.page_number = None
            self.page_load_time = None

    def __init__(self,machine_size,page_size):
        self.frame_number = machine_size//page_size
        # frame table entry
        self.fte = [self.Frame(_) for _ in range(self.frame_number)]
        # maintain an array of arrays to book keeping least recently used time and frame number
        self.used_order = []
        for frame_ind in range(self.frame_number-1,-1,-1):
            self.used_order.append([0,frame_ind])

    # check whether a specific page of a process is in the frame
    # returns two param, a boolean representing the existence, and the index of the frame in frame table entry
    def is_in_frame(self,process,word_location):
        for i in range(len(self.fte)):
            frame = self.fte[i]
            if frame.occupied_process == process and frame.word_range[0] <= word_location <= frame.word_range[1]:
                return True,i
        return False,-1

    # check whether the frame table entry is full
    # returns two params, the occupation status of frame, and the index of
    # highest available frame number if exist, otherwise return -1.
    def is_full_and_highest_avail_frame(self):
        for i in range(len(self.fte)-1,-1,-1):
            # spotted clear
            if self.fte[i].is_occupied == False:
                return False,i
        return True,-1

    # find the least recently used victim frame, only call this method when frame table entry is full and has to evict process
    def least_recently_used_frame(self):
        return self.used_order[0][1] # array of arrays, element format: [recent_used_time, frame]

    # random select a victim frame, only call this method when frame table entry is full and has to evict process
    def random_select_frame(self):
        return next_random_number()%len(self.fte)

    # select the latest frame as victim, only call this method when frame table entry is full and has to evict process
    def last_in_first_out_frame(self):
        return 0

class Process:
    def __init__(self,process_number,process_size,A,B,C):
        global N
        self.w = None # current word
        self.process_number = process_number
        self.process_size = process_size
        # control flow params specified by job mix number
        self.A = A
        self.B = B
        self.C = C
        self.next_word = None # only applies to job mix 4
        self.remaining_instructions = int(N)
        # self.load_and_eviction = []
        self.status = 'uninitialized'
        self.fault_counter = 0
        self.eviction_count = 0
        self.page_load_evict = {} # key: page number value: Page data structure
        self.termination_time = None
        self.cur_random_number = None

    # calculate the reference of current process to next word
    def next_word_reference(self):
        global job_mix
        self.cur_random_number = next_random_number()
        if show_random:
            print(self.process_number,'uses random number:',self.cur_random_number)
        if job_mix == 4:
            RAND_MAX = 2147483648
            y = self.cur_random_number / RAND_MAX
            if y < self.A:
                self.w = (self.w + 1) % int(S)
            elif y < self.A + self.B:
                self.w = (self.w - 5) % int(S)
            elif y < self.A + self.B + self.C:
                self.w = (self.w + 4) % int(S)
            elif y >= self.A + self.B + self.C:
                self.cur_random_number = next_random_number()
                self.w = self.cur_random_number % int(S)
                if show_random:
                    print(self.process_number,'uses random number:',self.cur_random_number)

    # calculate the current word reference
    def make_action(self):
        global job_mix
        global S # size of each process
        global global_time

        if self.status == 'terminated':
            self.termination_time = global_time
            return -1

        elif job_mix == 1:
            if self.status == 'uninitialized':
                self.w = (self.process_number * 111) % int(S)
                self.status = 'loaded'
            else:
                self.w = (self.w+1) % int(S)
            return self.w

        elif job_mix == 2:
            if self.status == 'uninitialized':
                self.w = (self.process_number * 111) % int(S)
                self.status = 'loaded'
            else:
                self.w = (self.w+1) % int(S)
            return self.w

        elif job_mix == 3:
            if self.status == 'uninitialized':
                self.w = (self.process_number * 111) % int(S)
                self.status = 'loaded'
            else:
                self.w = next_random_number() % int(S)
            return self.w
        elif job_mix == 4:
            if self.status == 'uninitialized':
                self.w = (self.process_number * 111) % int(S)
                self.status = 'loaded'
            return self.w

    # decrement the remaining insturction count
    def decrease_remaining_instruction(self):
        self.remaining_instructions -= 1
        if self.remaining_instructions <= 0:
            self.status = 'terminated'

class Page:
    def __init__(self):
        self.status = 'unloaded'
        self.load_time = None
        self.running_sum = 0

    def eviction_recording(self,time):
        self.running_sum += time - self.load_time
        self.load_time = None
        self.status = 'unloaded'

    def update_load_time(self,load_time):
        self.load_time = load_time
        self.status = 'loaded'

# generate a list of processes based on job mix (control flows of each process)
def generate_process_lst(process_size,job_mix):
    process_lst = []
    if job_mix == 1:
        process_num,A,B,C = 1,1,0,0
        process_lst.append(Process(process_num,process_size,A,B,C))
    elif job_mix == 2:
        process_num,A,B,C=4,1,0,0
        for i in range(1,process_num+1):
            process_lst.append(Process(i,process_size,A,B,C))
    elif job_mix == 3:
        process_num,A,B,C=4,0,0,0
        for i in range(1,process_num+1):
            process_lst.append(Process(i,process_size,A,B,C))
    elif job_mix == 4:
        p1 = Process(1,process_size,0.75,0.25,0)
        p2 = Process(2,process_size,0.75,0,0.25)
        p3 = Process(3,process_size,0.75,0.125,0.125)
        p4 = Process(4,process_size,0.5,0.125,0.125)
        process_lst = [p1,p2,p3,p4]
    return process_lst

# load the random number in a global variable,
# and initialize a global index to record reading progress
def load_random_number():
    global random_number_lst
    global random_number_index
    in_f = open('random-numbers.txt','r')
    random_number_index = 0
    random_number_lst = in_f.readlines()
    in_f.close()

# get the next random number from the global random number
def next_random_number():
    global random_number_index
    global random_number_lst
    res = int(random_number_lst[random_number_index].rstrip())
    random_number_index += 1
    return res

# check whether all processes are terminated
def process_termination_check(process_lst):
    for p in process_lst:
        if p.status != 'terminated':
            return False
    return True

if __name__ == "__main__":
    if len(sys.argv) <= 7:
        print('Please specify the following variables as commandline arguments:')
        print('M - machine size in words')
        print('P - the page size in words')
        print('S - the size of each process')
        print('J - the type of job mix')
        print('N - the number of references for each process')
        print('R - the replacement algorithm: lru, random, or fifo')
        print('V - verbose option: 0 for regular, 1 for verbose, 11 for show random and verbose\n')
        print('Usage: python3 paging.py M P S J N R V')
        exit(1)

    global_time = 1
    f_name,M,P,S,J,N,R,debugging_level = sys.argv

    if debugging_level == '1':
        verbose_option = True
        show_random = False
    elif debugging_level == '11':
        verbose_option = True
        show_random = True
    else:
        verbose_option = False
        show_random = False


    # output the setup detail
    print('The machine size is ',M,'.',sep='')
    print('The page size is ',P,'.',sep='')
    print('The process size is ',S,'.',sep='')
    print('The job mix number is ',J,'.',sep='')
    print('The number of references per process is ',N,'.',sep='')
    print('The replacement algorithm is ',R,'.',sep='')
    print('The level of debugging output is',debugging_level)
    load_random_number()
    frame_table_entry = FrameTable(int(M),int(P))
    job_mix = int(J)
    process_lst = generate_process_lst(int(P),int(J))
    all_process_terminate = False
    page_size = int(P)

    quantum = 3 if job_mix!=1 else 1

    while not all_process_terminate:
        all_process_terminate = process_termination_check(process_lst)
        for p in process_lst:
            for q in range(quantum):
                word_location = p.make_action()
                process_num = p.process_number
                in_frame_flag, hit_frame_index = frame_table_entry.is_in_frame(p, word_location)
                is_full_flag, highest_avail_frame_index = frame_table_entry.is_full_and_highest_avail_frame()
                # the current process is terminated
                if word_location == -1:
                    continue
                # if the word is in frame
                elif in_frame_flag:
                    if verbose_option:
                        # debugging msg
                        print(process_num,'references word ' + str(word_location) +' (page ' + str(word_location//page_size) +')' +' at time: ' + str(global_time) +': Hit in frame ' + str(hit_frame_index))

                    for i in range(len(frame_table_entry.used_order)):
                        recent_used_time,frame_ind = frame_table_entry.used_order[i]
                        if frame_ind == hit_frame_index:
                            frame_table_entry.used_order[i][0] = global_time
                            frame_table_entry.used_order.sort()

                    p.decrease_remaining_instruction()
                    p.next_word_reference() # get random number for next word reference

                # the page is not loaded in frame, check whether there is free frames in the table
                elif not is_full_flag:
                    for i in range(len(frame_table_entry.used_order)):
                        recent_used_time,frame_ind = frame_table_entry.used_order[i]
                        if frame_ind == highest_avail_frame_index:
                            frame_table_entry.used_order[i][0]=global_time
                            frame_table_entry.used_order.sort()

                    if verbose_option:
                        # debugging msg
                        print(process_num,'references word ' + str(word_location) +' (page ' + str(word_location//page_size) +') at time: ' + str(global_time) +': Fault, using free frame ' + str(highest_avail_frame_index) +'.')
                    frame = frame_table_entry.fte[highest_avail_frame_index]
                    frame.is_occupied = True
                    frame.occupied_process = p
                    frame.word_range = word_location//page_size * page_size, word_location//page_size * page_size + page_size-1
                    p.decrease_remaining_instruction()
                    p.fault_counter += 1

                    # document the page number and loading time
                    page_number = frame.word_range[0]//page_size
                    if page_number in p.page_load_evict:
                        p.page_load_evict[page_number].update_load_time(global_time)
                    else:
                        page = Page()
                        page.update_load_time(global_time)
                        p.page_load_evict[page_number] = page
                    p.next_word_reference() # get random number for next word reference

                # the page is not loaded in frame, select an victim and replace it
                else:
                    if R == 'lru': # Replacement algorithm is least recently used
                        victim_frame_index = frame_table_entry.least_recently_used_frame()

                        for i in range(len(frame_table_entry.used_order)):
                            recent_used_time, frame_ind = frame_table_entry.used_order[i]
                            if frame_ind == victim_frame_index:
                                frame_table_entry.used_order[i][0] = global_time
                                frame_table_entry.used_order.sort()

                    elif R == 'random': # Replacement algorithm is random select
                        victim_frame_index = frame_table_entry.random_select_frame()

                    else: # Replacement algorithm is LIFO
                        victim_frame_index = frame_table_entry.last_in_first_out_frame()

                    victim_process = frame_table_entry.fte[victim_frame_index].occupied_process
                    victim_process.eviction_count += 1

                    # record the eviction on the victim page
                    evicting_page = frame_table_entry.fte[victim_frame_index].word_range[0]//page_size
                    victim_process.page_load_evict[evicting_page].eviction_recording(global_time)
                    if verbose_option:
                        # debugging msg
                        print(process_num, 'references word '+str(word_location)+' (page ' + str(word_location//page_size) +') at time: '+str(global_time)+': Fault, evicting page', frame_table_entry.fte[victim_frame_index].word_range[0]//page_size,'of',victim_process.process_number,'from frame',str(victim_frame_index)+'.')

                    # evict_frame
                    frame = frame_table_entry.fte[victim_frame_index]
                    frame.occupied_process = p
                    frame.word_range = word_location//page_size * page_size, word_location//page_size * page_size + page_size-1

                    # document the page number and loading time
                    page_number = frame.word_range[0]//page_size
                    if page_number in p.page_load_evict:
                        p.page_load_evict[page_number].update_load_time(global_time)
                    else:
                        page = Page()
                        page.update_load_time(global_time)
                        p.page_load_evict[page_number] = page

                    p.decrease_remaining_instruction()
                    p.fault_counter += 1
                    p.next_word_reference() # get random number for next word reference
                global_time += 1

    overall_eviction = 0
    overall_total_running_sum = 0
    overall_fault = 0
    print()
    for p in process_lst:
        overall_eviction += p.eviction_count
        overall_fault += p.fault_counter
        process_total_running_sum = 0
        for key in p.page_load_evict.keys():
            page = p.page_load_evict[key]
            process_total_running_sum += page.running_sum

        average_residency = process_total_running_sum / p.eviction_count if p.eviction_count != 0 else 'undefined'
        overall_total_running_sum += process_total_running_sum
        if average_residency != 'undefined':
            print('Process ',p.process_number,' has ',p.fault_counter,' faults and ',average_residency,' average residency.',sep='')
        else:
            print('Process ',p.process_number,' has ',p.fault_counter,' faults.',sep='')
            print('\tWith no evictions, the average residence is undefined.')
    overall_average_resident = overall_total_running_sum / overall_eviction if overall_eviction != 0 else 'undefined'
    if overall_average_resident != 'undefined':
        print('\nThe total number of faults is ',overall_fault,' and the overall average residency is ',overall_average_resident,'.',sep='')
    else:
        print('\nThe total number of faults is ', overall_fault,'.',sep='')
        print('\tWith no evictions, the overall average residence is undefined.')