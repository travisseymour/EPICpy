# Contributing

Thank you for your interest in contributing to EPICpy!

The document is for those who wish to contribute to the Python codebase hosted in [EPICpy Github Repo](https://github.com/travisseymour/EPICpy). Feel free to suggest small changes such as typos and related corrections, moderate refactorings or tweaks, or even larger things like new features or large-scale refactoring.

Although it is fine to submit pull-requests for typos and other very minor changes, please either open an Issue on our Github repo to discuss your plans to make any larger changes to the code to gauge support from the EPICpy maintainers. Alternatively, check out the open Issues and let us know if you would like to contribute to one of those. We would like to avoid people creating larger pull requests for changes that won't be accepted. Just let us know what you're thinking first.

Please note that the C++ code on the EPICpy repository are just header files needed for our Python code to work with the compiled EPICLib dynamic libraries. You cannot alter the operation of EPICLib by making changes to the C++ files distributed with EPICpy. If you want to make changes to C++ code that is used for EPICLib, you should be contributing to [David Kiera's EPIC project](https://github.com/dekieras/EPIC).

### Overview

Contributing requires a basic understanding of how Git works and how Github works. You can learn more on the [Get Started With Github](https://guides.github.com/activities/hello-world/) page. The instructions below assume you want to work from the commandline. Some will instead prefer to use a more graphical Git workflow via an IDE such as [PyCharm](https://www.jetbrains.com/pycharm/), [VSCode](https://vscodium.com/), or git-specific tools such as [GitHub Desktop](https://desktop.github.com/) or [Tower](https://www.git-tower.com/mac). Either way, you can get started with the commandline approach below.

Before we get started, here is the overview:

- Fork (i.e., copy) the EPICpy repository to a repository your own Github account online.
- Clone (i.e., copy) your fork of EPICpy to your computer, e.g., `git clone ADDRESS-TO-REPOSITORY-YOU-WANT-TO-CLONE`
- cd into that folder.
- Create a new branch with `git branch YOUR-BRANCH-NAME`
- Make your code changes with your text editor.
- When finished, stage your cahgnes with `git add CHANGED-FILENAME` and commit your changes with a message using `commit -m "YOUR-COMMIT-MESSAGE"`.
- Switch back to the main branch with `git checkout main`.
- Verify this and remind yourself of your branch's name using `git branch`
- Push your newly committed (local) changes up to your forked repository on Github using `git push origin YOUR-BRANCH-NAME`
- Go to Github on the page where you have your fork of EPICpy and create a new Pull Request.
- Now you're waiting on the EPICpy maintainers to get back to you.

Before you subsequently create a new branch and make more changes, get synced up with the original EPICpy repository

- make sure you are back on your main branch using `git checkout main`
- pull down any changes from origin (orig EPICpy rep) using `git fech upstream` then `git checkout main` then `git merge upstream/main` then `git push` then `git rebase main`
- delete your old branches (you should start new branches from main, this will help encourage that practice). Check the branch(es) you have with `git branch` and then delete them by name `git branch -d YOUR-BRANCH-NAME`. Don't delete the main branch!


### Getting Setup

**First, Go to the Github Website and Fork the EPICpy Repository**

1. [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) EPICpy from the original repository. To do this, log into your own Github account and then go to the original EPICpy repository by clicking this link: [https://github.com/travisseymour/EPICpy](https://github.com/travisseymour/EPICpy). In the upper right-hand corner click the [Fork] link and then select your github account name to fork the EPICpy repo into your account (you're basically making a copy of it).

<mark>**NOTE**: The following commands should be typed into a command prompt or terminal window on your computer (i.e., not on the website):</mark>

**Copy the fork you just made to your computer, so you can work on it locally**

2. Type `git clone`, and then URL to your Fork of EPICpy. It will look like this, with **your** GitHub username instead of `YOUR-USERNAME`:
   ```bash
   $ git clone https://github.com/YOUR-USERNAME/EPICpy.git
   ```
3. This will create a directory called `EPICpy`, change to it, e.g.:
    ```bash
   $ cd EPICpy
    ```
4. Add the upstream and sync your fork from it.
   ```bash
   $ git remote add upstream https://github.com/travisseymour/EPICpy.git
   $ git remote -v
   $ git fetch upstream
   ```
   
**Make Sure You Have A Working Development Environment**

6. In order to actually be able to run EPICpy so that you can properly contribute to its development, you'll need to set up the necessary development environment. This is not the appropriate place to describe that process, but you can learn how in [this section](https://travisseymour.github.io/EPICpyDocs/epicpy_development_setup/) of the EPICpy documentation.

### Making Changes

**Making Edits To Your Cloned Fork**

6. First create a branch to hold your changes (it's not best practice to make edits directly to the main branch). Change YOUR-BRANCH-NAME below:
   ```bash
   # Make sure you are branching from main
   $ git checkout main
   # Create a new branch
   $ git branch YOUR-BRANCH-NAME
   # Switch to your new branch
   $ git checkout YOUR-BRANCH-NAME
   ```
8. To make changes to one of the Python code files within your new EPICpy branch, you can technically use any plain-text editor. However, it is advisable to use a programmer's text editor such as [Sublime Text](https://www.sublimetext.com/), or [Atom](https://atom.io/). Alternatively, you could use the built-in text editor as part of a programmer's Integrated Development Environment such as [PyCharm](https://www.jetbrains.com/pycharm/) or [VSCode](https://vscodium.com/).

9. Create a local commit by staging the file(s) you edited. Change `EDITED-FILE-NAME` below. Alternatively, you can add all files with `git add *` if you changed multiple files. Also make sure you add a short message describing the change you made:
   ```bash
   # Double check which files have been changed but have yet to be staged
   $ git status
   # Stage the changed file
   $ git add EDITED-FILE-NAME
   # Commit the changes to your branch with a short description of what changed.
   $ git commit -m "This is a short explanatory message about my change."
   ```
10. Now push this commit to your fork on Github. You will need to provide your Github username and password for this step.
    ```bash
    $ git push
    ```
For security reasons, GIT may ask you to create a Personal Access Token to use instead of your password. If so, use [these instructions](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token). 

### Submitting Changes

**Submit Your Changes to the Maintainers of EPICpy for Inclusion Using a Pull-Request.**

10. Your changes are currently only on your computer, so let's push them up to your fork on Github:
    ```bash
    # Switch back to the main branch
    $ git checkout main
    # Remind yourself what your branch is called if you forgot
    $ git branch
    # Push your changes up to your fork repo
    $ push origin YOUR-BRANCH-NAME
    ```
12. Go back to your browser and navigate to `https://github.com/YOUR-USERNAME/EPICpy` and click the **Pull Requests** tab. Now click the green **New Pull Request** button. Github will check your EPICpy fork against the official EPICpy repository and highlight the changed files. Double-check the title (and optionally add a longer description -- usually not needed) and then press the green button to submit your pull request.
13. At this point, you are waiting for the maintainers of EPICpy to accept and merge your changes into the official EPICpy repository.

## Keeping Your Fork Up To Date

Before making any subsequent changes, you should update your fork with the latest upstream changes (we set upstream to the original EPICpy repository in an earlier step). You'll need to first fetch the upstream repo's branches and latest commits to bring them into your repository:

```bash
# Fetch from upstream remote
$ git fetch upstream
# get on the main branch
$ git checkout main
# merge your local repo with the upstream repo (official EPICpy)
$ git merge upstream/main
# now sync your local repo with your fork of EPICpy on Github
$ git push
$ git rebase main
```

Now, your local main branch should be up-to-date with everything that has been modified upstream (by you via an accepted pull request or changes made by others).

## Other Considerations

**Deleting Old Branches**

Once you have gotten a branch merged with the official EPICpy repository, you should stop using that branch. The next set of changes you make should be to a **new** branch created off of the main branch. Thus, it is advisable to delete old branches:

```bash
# Remind yourself which branches you have
$ git branch
# Delete a branch
$ git branch -d YOUR-BRANCH-NAME
```

**Pull Requests of Branches With Lots of Commits**

If you are like most programmers, you are making multiple commits to a branch before you are at the point where you are ready to commit. It is best practice to consider combining (aka "squashing") multiple related commits into a smaller number of commits (or even a single commit). This is a more advanced topic; you can learn more about what this is and how to do it manually by reading articles like [this overview](https://medium.com/twodigits/keep-your-git-commit-history-clean-with-squash-f4886790a4c9) or [this detailed guide](https://medium.com/@slamflipstrom/a-beginners-guide-to-squashing-commits-with-git-rebase-8185cf6e62ec).

Squashing is not required, but if you are liberal with commits, you might consider the work required by the maintainers to read through 40 commits to understand a single pull-request.

# Communicating With Us

Feel free to comment on code or discuss issues with EPICpy's current operation (or request features) on the repository's Issue Tracker. For more general points and conversations, please use the Discussion page. We may move topics posted on either page to the other one if we feel a topic has either been misplaced, or the discussion evolves to the point where it would be better hosted on the other.