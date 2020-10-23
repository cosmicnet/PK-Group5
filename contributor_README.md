# Contributor Guide

Thank you for joining us to work on this project! We hope that here you will find useful information to help you get started. If you think of anything that should be added, feel free to create an issue and propose the change.

## Setting up virtual environment
To avoid confusion about which versions of python and any packages are being used, it's a good idea to work in a *virtual environment*.
Here's how to set one up:

```bash
python3 -m venv venv
source venv/bin/activate
```

Then you can install the packages required for working on the library straight from the requirements.txt file:

```bash
pip install -r requirements.txt
```

## Workflow 
Pick an issue to work on and assign yourself to that issue. 

Check out a new branch by typing in the console
```bash
git checkout -b <branch name>
```
Replace the contents of <> with your chosen branch name. It should include the number of the issue you've chosen to work on, as well as a short description of the issue in a few words. 

After making your improvements, run `git diff` in the console to satisfy yourself that you haven't changed anything other than what you intended to. Add and commit any changed files with an informative commit message beginning with a reference to the issue number:
```bash
git add <filename1> <filename2> <...>
git commit -m "#<issue number> <description of changes>"
```
Then you can push those changes to your branch:
```bash
git push origin <branch name>
```
The console will print out a link which you can follow to create a pull request. Another contributor will then review your changes and merge them into the master branch, or ask you to make some more changes before merging. 

If you are working on a branch for long periods of time, it can be a good idea to regularly merge the master branch into it so you stay up to date with the changes others have made in the meantime. To do this, type:
```bash
git pull
git merge origin/master
```

If Git finds any conflicts that it can't sort out automatically, it will helpfully mark these for you. Open the file that git complains about (e.g. `CONFLICT (content): Merge conflict in <filename>`), find the conflicting lines, and resolve the conflict in whatever way you see fit. Make sure to remove the many flags that Git has added to point you towards the conflict!
You can then add and commit the resolved file and push to your branch as described above, and keep working in your branch!


## Style guide

### Linting

Additions to the code should adhere to the [PEP8 Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/#introduction, "PEP8 Style Guide"). GitHub automatically tests your style with the Flake8 linter everytime you submit a pull request. We reccommend linting your code while you write it as this can save time and commits later on! To enable linting with Flake8 in Visual Studio Code, open the Command Palette (<kbd>&#8679;</kbd><kbd>&#8984;</kbd><kbd>P</kbd> or <kbd>CTRL</kbd><kbd>SHIFT</kbd><kbd>P</kbd>) and click on the **Python: Select Linter** command. You can then select Flake8 from the dropdown list. 

Unless there is a good reason for ignoring the linter, your pull request will not be granted until it passes these checks. The error messages are usually quite informative, but if you are not able to fix the issue you can contact a member of the core delelopment team who will be happy to help.⇧

### Naming conventions

Most methods and functions have one-word names. Where the name consists of multiple words, these are connected by an underscore. 
Parameter names are consistent with the variables of the model equations that form the base of [this library's functionalities](https://github.com/smf541/PK-Group5#about, "Functionality"). 

### Documentation

The online documentation is created with Sphinx and hosted on [Read the Docs](https://pk-model.readthedocs.io/en/latest/, "Documentation") and is updated automatically at each pull request. It is set up to reflect the state of the master branch, so any changes you make to a side branch will not show up until they have been merged into the master. 

Sphinx simply extracts the docstrings from each file in the code directory `pkmodel`, so please make sure your docstrings are informative. Ideally they should:

* succinctly describe the main functionality of the class, function or property that you are documenting,
* list, briefly describe and give the type of each input parameter along with any defaults, and
* do the same for each output.