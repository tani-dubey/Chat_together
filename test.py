class link_list:
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution:
    def deleteMiddle(self, head):
        fast,slow=head,head

        while fast and fast.next:
            if fast.next.next.next==None or fast.next.next ==None:
                slow.next=slow.next.next
                return head
            else:
                slow=slow.next
                fast=fast.next.next
        return None
    
node1=link_list(1)
node2=link_list(3)
node3=link_list(4)
node4=link_list(7)
node5=link_list(1)
node6=link_list(2)
node7=link_list(6)

node1.next=node2
node2.next=node3
node3.next=node4
node4.next=node5
node5.next=node6
node6.next=node7

obj=Solution()
ans=obj.deleteMiddle(node1)

while ans:
    print(ans.val,end="=>")
    ans=ans.next