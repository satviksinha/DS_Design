# Design Data Structure - Strings Collection

## About the Implementation

- The data structure used for storing the collection of strings is a trie. I have used two tries, one for the `prefix queries` and one for the `suffix queries`.
- Each trie node, contains the count of the number of words with prefix/suffix till that node in the `node.count` variable and the number of words ending at that node in the `node.word_finished` variable
- In addition, the `node.ids` set is used to keep track of the unique ids of the strings ending at that node
- The trie data structure efficiently gives the count of the number of words with the specified prefix/suffix
- The `remove` function will be explained in the `Smart Design Choices` section
- The methods of the class that make changes to the variable's values are protected by acquiring a lock so that the condition of `dirty write` doesn't happen


## Limitations/Tradeoffs

- The time taken by the `remove` method is higher than the other methods because we need to iterate through each string that has to be removed and also check if the string with this id was already removed or not. If it was already removed by some other instance, then we don't remove it again.
- When deleting a string from the prefix trie, it also has to be deleted from the suffix trie

## Smart Design Choices

<img src="trie.png">

I have used two tries as the data structures to assist with the prefix and suffix queries. The time taken to get the number of words starting/ending with the prefix/suffix is O(n) where n is the length of the prefix/suffix. This time complexity is pretty efficient compared to other data structures.

I had to give unique IDs to the node containing the last letter of every word. This was to aid in the creation of the remove function. Suppose, we inserted some words in the trie and then created two result instances with the query of the same prefix string. We'll get some results. Then we add the same strings again in the trie, and after adding these strings, we call the remove function on one of the instances. The strings get removed from the collection. 

Now, when we call the remove function from the other result instance, there are still strings that can be removed because we added the same strings again. But the key point here is that they were added after the generation of the result instance. These strings had already been removed by the first result instance and hence don't have to be removed again. For this purpose, we need some identification for each string so that we can differentiate between strings even if they have the same value. Since Python doesn't support pointers, I made use of an id-system, wherein I declared a static variable and gave unique IDs to each word. If some word has already been removed, we'll find that its id is no longer in the `node.ids` attribute and hence we don't need to remove it again.

A tuple consisting of the string and the unique ID of each string is stored in the Result class to aid with the removal of the string from the string collection.

The depth-first-search technique was used to get the strings from the tries. The time taken by the `remove` method would be of the order of O(m*h) where m is the size of the query operation and h is the height of the trie.
