import threading

# create a trie node
class Node:
    # initialize trie node
    def __init__(self,char):
        self.char = char
        self.children = {}
        # count of words ending at this node
        self.word_finished = 0
        # count of words with prefix/suffix
        self.count = 0
        # stores the unique ids of the words ending at this node
        self.ids = set()

class StringIndex:
    id = 0
    def __init__(self):
        self.prefix_root = Node('')
        self.suffix_root = Node('')
        # lock for thread safety
        self.lock = threading.Lock() 

    # inserts word and returns the count of the word
    def insert(self,string):
        with self.lock:
            # insert in suffix trie
            node = self.suffix_root
            for char in reversed(string):
                if char in node.children:
                    node = node.children[char]
                else:
                    new_node = Node(char)
                    node.children[char] = new_node
                    node = new_node
                node.count += 1
            node.word_finished += 1
            # unique id for each word
            node.ids.add(StringIndex.id)
            StringIndex.id += 1

            # insert in prefix trie
            node = self.prefix_root
            for char in string:
                if char in node.children:
                    node = node.children[char]
                else:
                    new_node = Node(char)
                    node.children[char] = new_node
                    node = new_node
                node.count += 1
            node.word_finished += 1
            node.ids.add(StringIndex.id)
            StringIndex.id += 1

            # return the count of the words before the word was inserted
            return node.word_finished - 1
    
    # returns a result instance containing the list of strings with the given prefix
    def stringsWithPrefix(self,prefix):
        with self.lock:
            node = self.prefix_root
            for char in prefix:
                if char in node.children:
                    node = node.children[char]
                else:
                    return Result([],self.prefix_root,self.suffix_root,True,node.count)
            return Result(self._dfs(node,prefix,0),self.prefix_root,self.suffix_root,True,node.count)
    
    def stringsWithSuffix(self,suffix):
        with self.lock:
            node = self.suffix_root
            for char in reversed(suffix):
                if char in node.children:
                    node = node.children[char]
                else:
                    return Result([],self.prefix_root,self.suffix_root,False,node.count)
            return Result(self._dfs(node,suffix,1),self.prefix_root,self.suffix_root,False,node.count)
    
    def _dfs(self,node,word,flag):
        # result should contain the string,the unique ids of the strings
        result = []
        if node.word_finished:
            node_ids_copy = node.ids.copy()
            result.append((word,node_ids_copy))
        for char in node.children:
            # flag = 0 means prefix, flag = 1 means suffix
            if flag == 0:
                result.extend(self._dfs(node.children[char],word+char,flag))
            else:
                result.extend(self._dfs(node.children[char],char+word,flag))
        return result

    
class Result:
    def __init__(self,strings,pre,suf,is_prefix,count):
        self.strings = strings
        self.prefix_root = pre
        self.suffix_root = suf
        # flag for checking if called by prefix /sufiix function
        self.is_prefix = is_prefix
        self.count = count
        self.lock = threading.Lock()

    def size(self):
        return self.count
    
    # remove strings from trie where node is the last word of the prefix
    def remove(self):
        with self.lock:
            # prefix part
            node = self.prefix_root
            pre_removed_strings = 0
            for string,ids in self.strings:
                for char in string:
                    node = node.children[char]
                # we've reached the end of the word now
                count = 0
                ids_copy = ids.copy()
                # check if these ids are present in the node
                for id in ids_copy:
                    if id in node.ids:
                        count += 1
                        # if id is present,remove it from the set
                        node.ids.remove(id)
                pre_removed_strings += count
                node.word_finished -= count
                node = self.prefix_root
                # decrement the count of prefixes by traversing again from top to bottom
                for char in string:
                    node = node.children[char]
                    node.count -= count
                node = self.prefix_root

            # suffix part-similar logic as prefix part
            node = self.suffix_root
            suf_removed_strings = 0
            for string,ids in self.strings:
                for char in reversed(string):
                    node = node.children[char]
                # we've reached the end of the word now
                count = 0
                ids_copy = ids.copy()
                for id in ids_copy:
                    if id in node.ids:
                        count += 1
                        node.ids.remove(id)
                suf_removed_strings += count
                node.word_finished -= count
                node = self.suffix_root
                for char in reversed(string):
                    node = node.children[char]
                    node.count -= count
                node = self.suffix_root
            
            if self.is_prefix:
                return pre_removed_strings
            else:
                return suf_removed_strings

# create a trie
trie = StringIndex()

# TEST-1 - for testing if the insert function works correctly and returns the correct count
print(f'{trie.insert("abc")} words before abc')
print(f'{trie.insert("abc")} words before abc')

# TEST-2 - for testing case sensitivity
print(f'{trie.insert("Abc")} words before Abc')

# TEST-3 - for testing the stringsWithPrefix function and the size function
result = trie.stringsWithPrefix('ab')
print(result.strings)
print(f'{result.size()} strings with prefix ab')

# TEST-4 - for testing the stringsWithSuffix function and the size function
result1 = trie.stringsWithSuffix('bc')
print(result1.strings)
print(f'{result1.size()} strings with suffix bc')

# TEST-5 - for testing the remove function
print(f'{trie.insert("abc")} words before abc')
print(f'{trie.insert("abc")} words before abc')
removed_strings = result.remove()
# only the strings present in result got removed
print(f'{removed_strings} strings removed from trie')
result2 = trie.stringsWithPrefix('ab')
# strings added after result was created are still intact
print(f'{result2.size()} strings with prefix ab')
print(f'{result2.remove()} strings removed from trie')
# removing from the same set again, leads to 0 strings getting removed
print(f'{result2.remove()} strings removed from trie')

# TEST-6 - multi-threaded concurrent insert operation
t1 = threading.Thread(target=trie.insert,args=('def',))
t2 = threading.Thread(target=trie.insert,args=('def',))
t3 = threading.Thread(target=trie.insert,args=('degd',))

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()

result3 = trie.stringsWithPrefix('de')
print(result3.strings)
print(f'{result3.size()} strings with prefix de')

# TEST-7 - testing concurrent removes
t1 = threading.Thread(target=result3.remove,args=())
t2 = threading.Thread(target=result3.remove,args=())

t1.start()
t2.start()

t1.join()
t2.join()

print(f'{result3.remove()} strings removed after threads called')

# TEST-8 testing concurrent insert and remove
t1 = threading.Thread(target=trie.insert,args=('xyz',))
t2 = threading.Thread(target=trie.insert,args=('xy',))
t3 = threading.Thread(target=trie.insert,args=('xyz',))

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()

result4 = trie.stringsWithPrefix('xy')

# concurrent remove and insert supported
t1 = threading.Thread(target=result4.remove,args=())
t2 = threading.Thread(target=trie.insert,args=('xy',))

t1.start()
t2.start()

t1.join()
t2.join()

print(f'{result4.remove()} strings removed after threads called')

# TEST-9 - testing for deadlock in concurrent stringsWithPrefix and stringsWithSuffix
trie.insert('xyz')
trie.insert('xyz')
trie.insert('yz')

t1 = threading.Thread(target=trie.stringsWithPrefix,args=('xy',))
t2 = threading.Thread(target=trie.stringsWithSuffix,args=('yz',))

t1.start()
t2.start()

t1.join()
t2.join()

# Similarly we get to know that concurrent operations on the same trie are supported
# for all methods and there is no situation where deadlock occurs, since before calling a write
# method, a lock is acquired and released after the operation is done.
