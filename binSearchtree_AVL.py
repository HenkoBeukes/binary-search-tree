# Self-balancing binary search tree (BST), with create, read, update and delete
# functionality and tree visualization.

# Copyright (C) 2019 by Henko Beukes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Credit is given to Edward Loper whose BST was used as a starting framework.
# His tree can be found here:
# http://code.activestate.com/recipes/577540-python-binary-search-tree/

#  The node structure is a list of lists (self._root) with the basic node being:
#  [[lo_child], [hi_child], value, sort_key] and each child having the same
#  structure.


import pickle
import time

_LO = 0
_HI = 1
_VALUE = 2
_KEY = -1


class BinarySearchTree(object):
    """
    A sorted collection of values that supports efficient insertion,
    deletion, and minimum/maximum value finding.  Values may be sorted
    either based on their own value, or based on a key value whose
    value is computed by a key function (specified as an argument to
    the constructor).

    BinarySearchTree allows duplicates -- i.e., a BinarySearchTree may
    contain multiple values that are equal to one another (or multiple
    values with the same key).  The ordering of equal values, or
    values with equal keys, is undefined.
    """

    def __init__(self, balance=True):
        """
        Create a new empty BST.  If balance is True the tree will self-balance after
        every insertion.
        """
        self._root = []  # starting with an empty node
        self._len = 0
        self.bal = balance  # sets if balancing is done with insert()

    def balance_factor(self, key):
        """
        Use as bst.balance_factor(key).
        Calculates the measure by which the tree is left or right heavy wrt 'the key'.
         bf <0 right heavy, 0> left heavy
        @param: key: The key or value to be used as a pivot.
        @return: an integer representing the measure of imbalance.
        """
        s = self._find(key)
        l = (flatten(s[0]))  # lower child node - w/o empty pos
        r = (flatten(s[1]))  # higher child node - w/o empty pos
        return (len(l)-len(r))//2

    def insert(self, value, key=None):
        """
        Use as bst.insert(value, key)
        Insert the specified value into the BST.
        If an explicit sort key is not specified, then each value is
        considered its own sort key.
        Balancing of the tree is also initiated during insert.
        """
        # Get the sort key for this value.
        if key is None:
            sort_key = value
        else:
            sort_key = key
        # Walk down the tree until we find an empty node.
        node = self._root
        stack = []  # sets a stack to track the recursion in the while loop
        while node:
            if isinstance(node[_KEY], list):
                continue
            else:
                if sort_key < node[_KEY]:
                    d = node[-1]
                    stack.append(d)
                    node = node[_LO]
                else:
                    d = node[-1]
                    stack.append(d)
                    node = node[_HI]

        # Put the value in the empty node.
        if sort_key is value:
            # Use slice assignment, to update source self._root .
            node[:] = [[], [], value]
        else:
            node[:] = [[], [], value, sort_key]
        self._len += 1
        if len(stack) > 2 and self.bal:
            for i in stack[1:]:
                self.balance(i)
            self.root_balance()

    def root_balance(self):
        """
        Use as bst.root_balance()
        Balance the tree around the root recursively until the bf is acceptable.
        If required a new root is created and the old root re-inserted.
        :return:
        """
        key = self._root[-1]
        bf = self.balance_factor(key)
        if bf < -2:
            old = self.pop(key)  # remove the old root
            self.insert(old[-2],old[-1])   # reinsert old root in an empty spot
            self.balance(key)
            self.root_balance()
        if bf > 2:
            old = self.pop(key)
            self.insert(old[-2],old[-1])
            self.balance(key)
            self.root_balance()
        else:
            return

    def balance(self, key):
        """
        Use as bst.balance(key)
        Balancing a node by either rotating left or right to reduce the balance
        factor.
        :param: key
        :return: function calls to rotate the node
        """
        bf = self.balance_factor(key)
        if bf < -1:
            return self.rotate_left(key)
        elif bf > 1:
            return self.rotate_right(key)

    def rotate_left(self, key):
        """
        Use as bst.rotate_left(key)
        Rotate a right heavy node to make the right child the root.
        :param key:
        :return:
        """
        old_root =[]
        new_root =[]
        s = self._find(key) # node to rotate
        old_root[:] = [s[0], s[1][0], s[2], s[-1]]
        new_root[:] = [old_root, s[1][1], s[1][2], s[1][-1]]
        s[:] = new_root

    def rotate_right(self, key):
        """
        Use as rotate_right(key)
        Rotate a left heavy node to make the laft child the root
        :param key:
        :return:
        """
        old_root = []
        new_root = []
        s = self._find(key)  # node to rotate
        old_root[:] = [s[0][1], s[1], s[2], s[-1]]
        new_root[:] = [s[0][0], old_root, s[0][2], s[0][-1]]
        s[:] = new_root

    def find(self, sort_key):
        """
        Use as bst.find(key)
        Find a value with the given sort key, and return it.  If no such
        value is found, then raise a KeyError.
        """
        return self._find(sort_key)[_VALUE]

    def pop(self, sort_key):
        """
        use as bst.pop(key)
        Find a value with the given sort key, remove it from the BST, and
        return it.  If multiple values have the same sort key, then it is
        undefined which one will be returned.  If no value has the
        specified sort key, then raise a KeyError.
        """
        result = self._pop_node(self._find(sort_key))
        return result[-2], result[-1]

    def keys(self, value=False, reverse=False):
        """
        Use as list(bst.keys())
        if value=False: Generate the node keys ordered either ascending or reverse.
        if value=True: Generate the node keys in sorted order with the values in a tuple,
        either ascending or reverse
        """
        if reverse:
            return self._iter(_HI, _LO, value)
        else:
            return self._iter(_LO, _HI, value)

    def update_node_data(self,sort_key, new_value=None, new_key=None):
        """
        Use as bst.update_node_date(key, new_value, new_key)
        Pops a node and changes the key, re-inserts it in the tree.
        @param sort_key:
        @return:
        """
        old = self.pop(sort_key)
        value = old[0]
        key = old[1]
        if new_value:
            value = new_value
        if new_key:
            key = new_key
        self.insert(value, key)

    def save_tree(self, file_name='data/saved_tree.bst'):
        """
        Use as bst.save_tree(file_name)
        Saves the self._root as a pickle
        :param file_name:
        :return:
        """
        with open(file_name, 'wb') as file:
            data = self._root
            pickle.dump(data, file)
            print('File saved')

    def load_saved_tree(self, file_name='data/saved_tree.bst'):
        """
        Use as load_saved_tree(file_name)
        Retrieves the saved pickle file.
        :param file_name:
        :return: data as a list
        """
        with open(file_name, 'rb') as file:
            data = pickle.load(file)
        return data

    __iter__ = keys

    def __len__(self):
        """Return the number of items in this BST , use as len(bst)"""
        return self._len

    def __nonzero__(self):
        """Return true if this BST is not empty"""
        return self._len > 0

    def __repr__(self):
        return '<BST: (%s)>' % ', '.join('%r' % v for v in self)

    def __str__(self):
        return self.pprint()

    def pprint(self, max_depth=7, frame=True, show_value=False):
        """
        Used when called as print(str(bst)).
        Return a pretty-printed string representation of this binary
        search tree.
        The max width is set at 160 which is the screen width.
        max_depth is set to 7, as deeper causes the tree to wrap on screen.
        """
        up, mid, dn = self._pprint(self._root, max_depth, show_value)
        lines = up + [mid] + dn
        if frame:
            width = min(160, max(len(line) for line in lines))
            s = '+-' + 'UPPER'.rjust(width, '-') + '-+\n'
            s += ''.join('| %s |\n' % line.ljust(width) for line in lines)
            s += '+-' + 'LOWER'.rjust(width, '-') + '-+\n'
            return s
        else:
            return '\n'.join(lines)

    def _find(self, sort_key):
        """
        Return a node with the given sort key, or raise KeyError if not found.
        """
        node = self._root
        while node:
            node_key = node[_KEY]
            if sort_key < node_key:
                node = node[_LO]
            elif sort_key > node_key:
                node = node[_HI]
            else:
                return node
        raise KeyError("Key %r not found in BST" % sort_key)

    def _pop_node(self, node):
        """
        Delete the given node from _root, and return its value and key.
        Reshuffle the tree to fill the empty spot
        :param node
        :return: node(value), node(key
        """
        n = node[-1]
        value = node[_VALUE]
        bf = self.balance_factor(n)
        if node[_LO]:
            if node[_HI]:
                if bf < 0:  # right heavy
                    """
                    This node has two children. Right child node becomes designate 
                    successor because right heavy. But if right child has a left 
                    child: lowest left child of right child becomes the successor.
                    """
                    successor = node[_HI]
                    while successor[_LO]:
                        """ There is a left child; cascade down the left side until 
                        there is no more left children, meaning successor will be 
                        smallest value larger than nodeX. 
                        """
                        successor = successor[_LO]  # last left child becomes the successor

                    node[2:] = successor[2:] # copy value & key of successor to new position

                    successor[:] = successor[_HI]
                    """move the old child of the successor into the successors old 
                    place, using slice assignment """

                else:   # left heavy or balanced
                    successor = node[_LO]  # If two children: Left is successor > left heavy
                    while successor[_HI]:
                        """ If left child has a right child; cascade until there 
                        is no more right children, meaning successor will be largest 
                        value smaller than nodeX
                        """
                        successor = successor[_HI]  # last right child becomes the successor
                    node[2:] = successor[2:]  # copy value & key of successor to new position

                    successor[:] = successor[_LO]
                    """move the old child of the successor into the successors old 
                    place using slice assignment """
            else:
                # This node has a left child only; replace it with that child.
                node[:] = node[_LO]
        else:
            if node[_HI]:
                # This node has a right child only; replace it with that child.
                node[:] = node[_HI]
            else:
                # This node has no children; make it empty.
                del node[:]
        self._len -= 1
        return value, n  # returns the value and key of the popped node

    def _iter(self, pre, post, value):
        """Helper for sorted iterators.
          - If (pre,post) = (_LO,_HI), then this will generate items
            in sorted order.
          - If (pre,post) = (_HI,_LO), then this will generate items
            in reverse-sorted order.
        Using an iterative implementation (rather than the recursive one)
        for efficiency.
        """
        stack = []
        node = self._root
        if value:
            result = 'node[_KEY], node[_VALUE]'
        else:
            result = 'node[_KEY]'
        while stack or node:
            if node:  # descending the tree
                stack.append(node)
                node = node[pre]
            else:  # ascending the tree
                node = stack.pop()
                yield eval(result)
                node = node[post]

    def _pprint(self, node, max_depth, show_value, spacer=4):
        if max_depth == 0:  # base condition
            return [], '- ...', []
        elif not node:
            return [], '- EMPTY', []
        else:
            up_lines = []
            dn_lines = []
            mid_line = '-%r' % node[_KEY]
            if len(node) > 3 and show_value:
                mid_line += ' (Val= %r)' % node(_VALUE)
            if node[_HI]:
                u, m, d = self._pprint(node[_HI], max_depth - 1, show_value)
                spacing_t = ' ' * (len(d) + spacer)
                up_lines += [spacing_t + line for line in u]
                up_lines.append(spacing_t + '/' + m)
                up_lines += [' ' * (len(d) - i +
                                     spacer - 1) + '/' + ' ' * (i + 1) +
                              line for (i, line) in enumerate(d)]
            if node[_LO]:
                u, m, d = self._pprint(node[_LO], max_depth - 1, show_value)
                spacing_b = ' ' * (len(u) + spacer)
                dn_lines += [' ' * (i + spacer) +
                              '\\' + ' ' * (len(u) - i) +
                              line for (i, line) in enumerate(u)]
                dn_lines.append(spacing_b + '\\' + m)
                dn_lines += [spacing_b + line for line in d]
            return up_lines, mid_line, dn_lines


def flatten(mylist):
    """Using an iterative flattening function as recursive flattening functions fail
    with a recursion depth error with large lists (1000 entries)
    The original list remains unchanged.
    @param mylist:
    @return: items (a flattened copy of mylist)
    """
    items = []
    items[:] = mylist
    for i, x in enumerate(items):
        while i < len(items) and isinstance(items[i], list):
            items[i:i+1] = items[i]
    return items


def instructions():
    """This function takes input from stdin and calls functions for:
    insert, find, update, delete, save file, retrieve file
    """
    choice = input("Please enter one of the following:\ni for insert a node.\nd to "
                   "delete a node\nf to find the data of a node\nu to change a node "
                   "value and/or key\ns to save a tree to file\nr to retrieve a tree "
                   "from file\n or press enter to quit\n:>")
    if choice == 'i':
        new_node = input("Please enter the data as: value, key\n")
        new_node = new_node.split(',')
        print(new_node)
        bst.insert(new_node[0],new_node[1])
    elif choice == 'd':
        dead_node = input("Please enter the node key to delete\n")
        bst.pop(dead_node)
    elif choice == 'f':
        # use time to compare durations of find() for different size trees
        wanted_node = input("Please enter the key of the node you seek\n")
        start = time.time()
        result = bst.find(wanted_node)
        print(result)
        end = time.time()
        duration = end-start
        print('duration:',duration)
    elif choice == 'u':
        old_node = input("Please enter the key of the node you want to update\n ")
        print(f"You want to change this node: {old_node}")
        new_value = input("Please enter the new value or press enter to move on\n")
        new_key = input("Please enter the new key or press enter to move on\n")
        bst.update_node_data(old_node, new_value=new_value, new_key=new_key)
    elif choice == 's':
        file = input("Please enter the file name you want to save it to or press enter "
                     "for default\n")
        if file:
            bst.save_tree(file)
        else:
            bst.save_tree()
    elif choice == 'r':
        file = input("Please enter the file name you want to use or press enter for "
                     "default:\n")
        if file:
            bst._root = bst.load_saved_tree(file)
        else:
            bst._root = bst.load_saved_tree()
    else:
        quit()


if __name__ == "__main__":
    with open('data/list500.bst', 'rb') as file:
        v = pickle.load(file)

    balance = input("Do you want the tree to be balanced?:y/n?\n")
    if balance == 'y':
        bst = BinarySearchTree()
    else:
        bst = BinarySearchTree(False)

    for v,k in v:
        bst.insert(v,k)
    print(str(bst))

    # print(list(bst.keys(value=False)))  # to print the list of keys

    while True:
        instructions()
        print(str(bst))


