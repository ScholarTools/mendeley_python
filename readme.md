# Mendeley Code For Python #
This repo implements the Mendeley API in Python. It also implements a client library. It will also implement library analysis code.

##Motivation##

My focus is on developing scripting access to my Mendeley data. As a simple example, I might wish to know which of my Mendeley entries are missing valid Pubmed IDs, and then remedy this by adding them. Doing this would help to ensure higher quality meta data for my entries. As another example, I might wish to know which of the references from a paper I am reading are in my library or not. By writing code we can make a query to the API for this information.

Mendeley provides a [Python API](https://github.com/Mendeley/mendeley-python-sdk). When originally implementing this code I found the API to be lacking. It (the Mendeley version) has since been updated substantially. 

At this point I find my version easier to understand although it is not fully implemented.

##Current Plans##

(as of February 25, 2016)

I'm currently working on another library (TODO: Insert link) for extracting references for a given paper. Once this is done, I'll be implementing code to analyze whether or not these references are in the library or not.

## Getting Started ##

1. Copy the config_template into a file config.py and fill in the appropriate values. This will require signing up for a [Mendeley API account](https://mix.mendeley.com/portal#/register). Importantly, the redirect API should be: **https://localhost**
2. Your library can then be loaded as:

```python
from mendeley import client_library
c = client_library.UserLibrary()
#c.docs will contain a pandas dataframe of your library
```

##Contributing##

I would love to get help in moving this code forward. If you're interested feel free to send me an email and we can chat! 

## Requirements ##

This needs some work but relies heavily on:
1. **Requests**
2. **Pandas**