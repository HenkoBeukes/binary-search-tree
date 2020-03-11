"""
A script to create a list of key value pairs to use in the bst. Saved  as a pickle in
the data folder.

"""
from random import choice
import pickle

number = 200
value_source = list("1234567890qwertyuiopasdfghjklzxcvbnm")
key_source = list("qwertyuiopasdfghjklzxcvbnm")

results = []
for i in range(1,number,1):
    value = []
    key = []
    for i in range(1,5,1):
        q = choice(value_source)
        value.append(q)
    for j in range(1, 4, 1):
        r = choice(key_source)
        key.append(r)
    value = ''.join(value)
    key = ''.join(key)
    results.append((value,key))

# print(results)

with open('data/list200.bst', 'wb') as file:
    pickle.dump(results, file)
    print('File saved')






