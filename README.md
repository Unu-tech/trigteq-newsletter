# trigteq_newsletter
Geology and mining newsletter and chatbot developed at trigteq

## Setting up local dev environment

### Step 0: When setting up a VM from scratch

<details>
<summary> You may ignore if pyenv installs fine </summary>

Setting up VM from scratch requires some additional installs. Assuming linux machine, do the following:

```bash
sudo apt-get update && sudo apt upgrade
# Following are needed for python installation with pyenv (may be redundant).
sudo apt-get install bzip2 libncurses5-dev libncursesw5-dev libffi7 libffi-dev \
 libreadline8 libreadline-dev zlib1g zlib1g-dev libssl-dev libbz2-dev libsqlite3-dev lzma liblzma-dev libbz2-dev

```

If there's an error due to version numbering, search for latest version. 

```bash
# E: Unable to locate package libreadline5

apt-cache search libreadline
```

</details>

### Step 1: Install pyenv 

**python local environment is managed by pyenv**. Follow the instructions [here](https://github.com/pyenv/pyenv). 

Once the installation on you machine done, install python version.

```bash
# install Python 3.11.5
pyenv install 3.11.5

# create new virtual environment (choose any name you like)
pyenv virtualenv 3.11.5 trigteq_newsletter

# On the root of the repository, set the new environment as the local environment
pyenv local trigteq_newsletter
```

### Step 2: install dependencies

The below command installs requirements-dev and what's under the src directory as packages

```bash
make install   # install dev dependencies
```

### Step 3: Start server

Note that env variables should be present. Then, run:

```bash
docker compose up -d
# When stopping
# docker compose down
# Can also restart
# docker compose restart
```
