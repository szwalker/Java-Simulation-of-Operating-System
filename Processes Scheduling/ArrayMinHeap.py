class ArrayMinHeap:
    class Item:
        def __init__(self, process):
            self.elem = process

        def __gt__(self, other):
            if self.elem.penalty_ratio > other.elem.penalty_ratio:
                return True
            elif self.elem.penalty_ratio == other.elem.penalty_ratio:
                if self.elem.A > other.elem.A:
                    return True
                elif self.elem.A == other.elem.A:
                    return self.elem.ind > other.elem.ind
            else:
                return False


    def left(self, j):
        return 2*j

    def right(self, j):
        return 2*j + 1

    def parent(self, j):
        return j // 2

    def swap(self, j1, j2):
        self.data[j1], self.data[j2] = self.data[j2], self.data[j1]

    def __init__(self):
        self.data = [None]

    def __contains__(self,process):
        flag = False
        for j in self.data:
            if j and process is j.elem:
                return True
        return flag


    def reorder(self):
        first_non_leaf_ind = self.parent(len(self.data)-1)
        for j in range(first_non_leaf_ind, 0, -1):
            self.fix_down(j)

    def __len__(self):
        return len(self.data) - 1

    def is_empty(self):
        return len(self) == 0

    def min(self):
        if(self.is_empty()):
            raise Exception("Priority queue is empty!")
        min_item = self.data[1]
        return min_item


    def insert(self, process):
        new_item = self.Item(process)
        self.data.append(new_item)
        self.fix_up(len(self.data) - 1)


    def fix_up(self, j):
        parent_ind = self.parent(j)
        if (j > 1) and (self.data[j] < self.data[parent_ind]):
            self.swap(j, parent_ind)
            self.fix_up(parent_ind)

    def extract_min(self):
        if (self.is_empty()):
            raise Exception("Priority queue is empty!")
        item = self.data[1]
        self.swap(1, len(self.data)-1)
        self.data.pop()
        self.fix_down(1)
        return item.elem

    def fix_down(self, j):
        left_ind = self.left(j)
        if (left_ind < len(self.data)):
            ind_of_smallest_child = left_ind
            right_ind = self.right(j)
            if(right_ind < len(self.data)):
                if (self.data[right_ind] < self.data[ind_of_smallest_child]):
                    ind_of_smallest_child = right_ind
            if (self.data[ind_of_smallest_child] < self.data[j]):
                self.swap(j, ind_of_smallest_child)
                self.fix_down(ind_of_smallest_child)

