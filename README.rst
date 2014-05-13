Mendeley Code for Python
--------------------------

This repo is meant to hold my Mendeley code for Python. The code is still just starting out. 

Motivation
--------------------

Mendeley is currently reworking a lot of aspects of their API, starting with a switch from OAuth 1 to OAuth 2. Other changes are promised in the near future. I'm not the biggest fan of the way `their API <https://github.com/Mendeley/mendeley-oapi-example>`_ is designed however and it doesn't support OAuth 2 (This might have changed recently).

The following is a rough layout of where I'd like to go with this code:

1. Finish implementation of all user specific methods. Public methods may be implemented as well.
2. Build test code!
3. Build in local database support for managing documents.
4. Add analysis functions that allow for data processing. As an example, perhaps we want to ensure that all documents have valid Pubmed IDs.

Getting Started
----------------------

1. Copy the config_template into a file config.py and fill in the appropriate values. This will require signing up for a `Mendeley API account <https://mix.mendeley.com/portal#/register>`_. Importantly, the redirect API should be: **https://localhost**
2. Run: **mendeley.auth.get_access_token(username:password)**
3. Create an instance of **mendeley.api.UserMethods** and call its functions.

JAH TODO: Provide code example.

Contributing
----------------------

I would love to get help in moving this code forward. If you're interested feel free to send me an email about how to best move forward. Alternatively, you are always welcome to make pull requests. I'm currently not very set in my ways and welcome any suggestions as to how things should be structured differently.

Requirements
----------------------

The code relies on the **Requests** package.

Documentation
-------------

Trying to follow:

https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

