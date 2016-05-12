#!/usr/bin/python
from collections import Counter

# Read in dois.txt and separate by commas
f = open('dois.txt', 'r')
dois = f.read().split(',')

# Remove all "" elements
dois = list(set(dois) - set(""))

prefixes = []
names = []

for x in range(len(dois)):
    if dois[x][2:5] != '10.':
        continue
    prefixes.append(dois[x][2:9])
    names.append(dois[x][2:-1])

# Count and return each unique prefix with the number of times it occurs
p = Counter(prefixes)
top = p.most_common(len(p))

'''
text = open('doi_to_provider.txt', 'a')
for x in range(0, len(top)):
    text.write(str(top[x]))
    text.write('\n')
'''


# Create list of DOIs with each unique prefix represented once, in decreasing order of occurrence
examples = []
for x in range(len(p)):
    pre = top[x][0]
    for y in range(len(prefixes)):
        if pre == prefixes[y]:
            examples.append(names[y])
            break

unique_prefixes = [x[0] for x in top]

print(examples)

'''
for x in range(len(prefixes)):
    if prefixes[x] == '10.1002':
        print(names[x])
'''
