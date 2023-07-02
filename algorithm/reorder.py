# -*- coding: utf-8 -*-
from audioop import reverse
from sre_parse import FLAGS
import numpy as np

class Locked_parts:
    
    def __init__(self,arr) -> None:
        if (len(arr)==0):
            self.locked_arr=[]
        else:
            self.locked_arr=[list(arr)]

    def connect(self,locked_parts):
        self.locked_arr+=locked_parts.get_arr()

    def get_arr(self):
        return self.locked_arr

    def check(self,insert_arr):
        if (len(self.locked_arr)==1):
            inboth=list(set(self.locked_arr[0]).intersection(set(insert_arr)))
            if (len(inboth)==len(self.locked_arr[0])):
                return 'full'
            elif (len(inboth)==0):
                return 'no'
            else:
                # def compare(a):
                #     """
                #         put involved element in the right side
                #     """
                #     if a in inboth:
                #         return 1
                #     return 0
                # self.locked_arr[0].sort(key=compare)
                return 'right'
        
        full_flag=True
        no_flag=True
        left_flag=True
        right_flag=True
        unpossible_count=0

        begin=self.locked_arr[0]
        end=self.locked_arr[-1]
        inboth_begin=list(set(begin).intersection(set(insert_arr)))
        inboth_begin=len(inboth_begin)/len(begin)
        inboth_end=list(set(end).intersection(set(insert_arr)))
        inboth_end=len(inboth_end)/len(end)
        if (inboth_begin==0):
            left_flag=False
        if (inboth_end==0):
            right_flag=False
        if (inboth_begin>0 and inboth_begin<1 and inboth_end>0 and inboth_end<1):
            unpossible_count=999



        for part in self.locked_arr:
            inboth=list(set(part).intersection(set(insert_arr)))
            if (len(inboth)>0 and len(inboth)!=len(part) and not full_flag and not no_flag):
                unpossible_count=999
            

            if (len(inboth)!=0):
                no_flag=False

            if (len(inboth)>0 and not full_flag):
                left_flag=False

            if (len(inboth)!=len(part)):
                if (len(inboth)>0):
                    unpossible_count+=1
                full_flag=False
            
            # 从左面=>left || full
            # 从右面=>right
        full_flag_back=True
        for part in reversed(self.locked_arr):
            inboth=list(set(part).intersection(set(insert_arr)))
            if (len(inboth)>0 and not full_flag):
                right_flag=False
            if (len(inboth)!=len(part)):
                full_flag_back=False

        if (full_flag): return "full"
        if (no_flag): return 'no'
        if (left_flag): return 'left'
        if (right_flag): return 'right'
        # if (unpossible_count>1): return 'unpossible'
        return 'unpossible'

    def split(self,direction,insert_arr):
        """
            direction = 'left' | 'right'
        """
        break_index=-1
        split_arr=[]
        left_arr=[]
        for index,part in enumerate(self.locked_arr):
            inboth=list(set(part).intersection(set(insert_arr)))
            if (len(inboth)>0 and len(inboth)!=len(part)):
                split_arr=inboth
                left_arr=list(set(part).difference(set(insert_arr)))
                break_index=index

        if (break_index==-1): return

        self.locked_arr.pop(break_index)

        if (direction=='left'):
            self.locked_arr.insert(break_index,left_arr)
            self.locked_arr.insert(break_index,split_arr)
        if (direction=='right'):
            self.locked_arr.insert(break_index,split_arr)
            self.locked_arr.insert(break_index,left_arr)


    def reverse(self):
        self.locked_arr.reverse()
        for part in self.locked_arr:
            part.reverse()


class Parts:
    """
    
    """
    def __init__(self,arr) -> None:
        self.locked_parts=[]
        self.unlocked_parts=list(arr)

    def to_json(self):
        return{
            "locked":list(map(lambda x:x.get_arr(), self.locked_parts)),
            "unlocked":self.unlocked_parts
        }

    def check(self,insert_arr):
        right_index_arr=[]
        left_index_arr=[]
        involved_full_parts_index_arr=[]
        for index,locked_part in enumerate(self.locked_parts):
            check_ans=locked_part.check(insert_arr)
            if (check_ans=='unpossible'):
                return False
            elif (check_ans=='no'):
                continue
            else:
                if (check_ans=='right'):
                    right_index_arr.append(index)
                elif (check_ans=='left'):
                    left_index_arr.append(index)
                elif (check_ans=='full'):
                    involved_full_parts_index_arr.append(index)
        if len(right_index_arr)+len(left_index_arr)>2:
            return False

        left_index=-1
        right_index=-1
        if (len(left_index_arr)==2):
            left_index=left_index_arr[1]
            right_index=left_index_arr[0]
            self.locked_parts[right_index].reverse()

        elif (len(right_index_arr)==2):
            left_index=right_index_arr[1]
            right_index=right_index_arr[0]
            self.locked_parts[left_index].reverse()

        else:
            if len(right_index_arr)==1:
                right_index=right_index_arr[0]
            if len(left_index_arr)==1:
                left_index=left_index_arr[0]
        
        self.insert_arr=insert_arr
        self.insert_param=(right_index,left_index,involved_full_parts_index_arr)

        return True

        

    def insert(self):
        (right_index,left_index,involved_full_parts_index_arr)=self.insert_param
        # involved_parts=[(check_ans,index)] self.locked_parts self.unlocked_parts

        new_full_locked=list(set(self.unlocked_parts).intersection(set(self.insert_arr)))
        self.unlocked_parts=list(set(self.unlocked_parts).difference(set(new_full_locked)))
        new_full_locked_part=Locked_parts(new_full_locked)

        if (right_index==-1):
            begin=Locked_parts([])
        else:
            begin=self.locked_parts[right_index]
        if (left_index==-1):
            end=Locked_parts([])
        else:
            end=self.locked_parts[left_index]
        begin.split('right',self.insert_arr)
        end.split('left',self.insert_arr)
        for full_part_index in involved_full_parts_index_arr:
            begin.connect(self.locked_parts[full_part_index])
        begin.connect(new_full_locked_part)
        begin.connect(end)

        # left split lock
        # right split lock
        # left.concact until right


        if (right_index!=-1):
            involved_full_parts_index_arr.append(right_index)
        if (left_index!=-1):
            involved_full_parts_index_arr.append(left_index)
        
        involved_full_parts_index_arr.sort(reverse=True)

        for i in range(len(involved_full_parts_index_arr)):
            self.locked_parts.pop(involved_full_parts_index_arr[i])

        self.locked_parts.append(begin)

        # right left full*n
        # pre_check => no || right || left
        # => right_check || left_check
        # locked_parts[i].connect && split

class Parts_2D:
    def __init__(self,question_all_arr,respondent_all_arr) -> None:
        self.q_parts=Parts(question_all_arr)
        self.r_parts=Parts(respondent_all_arr)

    def check(self,q_arr,r_arr):
        return self.q_parts.check(q_arr) and self.r_parts.check(r_arr)


    def check_and_insert(self,q_arr,r_arr):
        if (self.q_parts.check(q_arr) and self.r_parts.check(r_arr)):
            self.q_parts.insert()
            self.r_parts.insert()
            return True
        return False

    def to_json(self):
        return {
            'q_order':self.q_parts.to_json(),
            'r_order':self.r_parts.to_json()
        }


# tt=Parts_2D(list(range(10)),list(range(300)))
# tt.check_and_insert([2,3],[4,5,10,44])

# tt.check_and_insert([3,4,5],[44,43,10,58])


p=Parts(list(range(11)))

def check_and_insert(arr):
    print(p.check(arr))
    if (p.check(arr)):
        p.insert()
        print('now',p.locked_parts)



# check_and_insert([1,2,3])
# check_and_insert([1,2,7])
# check_and_insert([1,2,5])
# check_and_insert([0,1])

# # check_and_insert([8,5])
# # check_and_insert([2,4,3,9])

# check_and_insert([1,7,8,5])

# check_and_insert([2,3,4,5])
# # no need to consider the case of that the new cluster is included


