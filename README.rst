Mendeley Code for Python
--------------------------

This repo is meant to hold my Mendeley code for Python. I have the basic skeleton in place for making requests.

Motivation
----------

My focus is on developing scripting access to my Mendeley data. As a simple example, I might wish to know which of my Mendeley entries are missing valid Pubmed IDs, and then remedy this by adding them. Doing this would help to ensure higher quality meta data for my entries. As another example, I might wish to know which of the references from a paper I am reading are in my library or not. By writing code we can make a query to the API for this information.

Mendeley actually provides an example Python API (https://github.com/Mendeley/mendeley-python-sdk), but I find it to be lacking. Important differences include:

1) Documentation of all methods in the code. I'd rather be able to code with documentation in my IDE than needing to constantly check a website for details.
2) Actual methods to call, rather than dynamically created methods. This can help a bit with code completion, as well as allow flexibility where needed.
3) Responses are classes (optionally) with followup methods of their own.
4) Perhaps most importantly, the goal is to provide more than just Python bindings to the Mendeley API. At the same time, the API should be fully exposed in its own set of modules, rather than interspersed with analysis code.

Current Plans
--------------

1. Finish implementation of all user specific methods. Some public methods will be implemented as well as an example.
2. Build test code!
3. Build in local database support for managing documents.
4. Add analysis functions that allow for data processing.

Getting Started
----------------------

1. Copy the config_template into a file config.py and fill in the appropriate values. This will require signing up for a `Mendeley API account <https://mix.mendeley.com/portal#/register>`_. Importantly, the redirect API should be: **https://localhost**
2. Run: **mendeley.auth.get_access_token(username:password)**
3. Create an instance of **mendeley.api.UserMethods** and call its functions.

.. code:: python

	#This only needs to be run once
	from mendeley import auth, config
	du  = config.DefaultUser #This can be skipped if you want to type the inputs in directly
	auth.get_user_access_token_no_prompts(du.username,du.password)
	
	#Private Methods example
	from mendeley import api as mapi
	um  = mapi.UserMethods()
	lib_ids = um.docs_get_library_ids()
	
	#Public Methods Example
	pm = mapi.PublicMethods()
	ta = pm.get_top_authors()
	
Contributing
------------

I would love to get help in moving this code forward. If you're interested feel free to send me an email about how to best move forward. Alternatively, you are always welcome to make pull requests. I'm currently not very set in my ways and welcome any suggestions as to how things should be structured differently.

Requirements
------------

The code relies on the **Requests** package.

Documentation
-------------

Trying to follow:

https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

