# trigteq_newsletter
Geology and mining newsletter and chatbot developed at trigteq

## Setting up local dev environment

### Step 1: Install pyenv 

**python local environment is managed by pyenv**. Follow the instructions [here](https://github.com/pyenv/pyenv). 

Once the installation on you machine done, install python version.

```bash
# install Python 3.11.5
pyenv install 3.11.5

# create new virtual environment (choose any name you like)
pyenv virtualenv 3.11.5 trigteq_newsletter

# On the root of the repository, set the new environment as the local environment
pyenv local assign
```

### Step 2: install dependencies

The below command installs requirements-dev and what's under the src directory as packages

```bash
make install   # install dev dependencies

