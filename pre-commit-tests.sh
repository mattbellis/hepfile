#!/bin/bash

verbose=$(true)

echo "-------------------------------------------"
echo "        Beginning Pre-Commit Tests         "
echo "-------------------------------------------"

# stash unstaged commits
# recommended by: https://codeinthehole.com/tips/tips-for-using-a-git-pre-commit-hook/
# STASH_NAME="pre-commit-$(date +%s)"
# git stash save --quiet --keep-index --include-untracked $STASH_NAME

##################################################
# Run tests
##################################################
# run pytest and give exit code 1 if not successful

if [[ $verbose == $(true) ]]; then
    echo "1) Running Python Unit Tests"
    python tests/runtests.py --verbose 
else
    python tests/runtests.py 1>/dev/null
fi
ERR=$?

if [[ $verbose == $(true) ]]; then
    echo -e "\tPython tests finished with exit code $ERR"
fi

##################################################
# check for debug statements (we don't want these clogging our code)
echo -e "\n"
if [[ $verbose == $(true) ]]; then
    echo "2) Checking for superfluous debug statements"
fi

GREP_RESULT=$(grep "pdb" src/hepfile/*.py | tr "\n" "|" | sed s/"|"/"\n\t"/)
if [[ $GREP_RESULT ]]; then
    if [[ $verbose == $(true) ]]; then
       echo -e "\tFound a pdb statement:" 
       echo -e "\t$GREP_RESULT"
    fi	 
    ERR=1
else
    [ $verbose == $(true) ] && echo -e "\tNo debug statements found! Continuing..."
fi

##################################################
# run a linter
echo -e "\n"
if [[ $verbose == $(true) ]]; then
    echo "3) Running pylint"
fi

PYLINT_RESULT=$(pylint --errors-only hepfile | tr "\n" "|" | sed s/"|"/"\n\t"/)
if [[ $PYLINT_RESULT ]]; then
    if [[ $verbose == $(true) ]]; then
	echo -e "\tWARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	echo -e "\tpylint found some possible errors!"
	echo -e "\tCommit will continue, but be cautious!"
	echo -e "\tPlease check the following pushing:"
	echo -e "\t$PYLINT_RESULT"
    fi
    #ERR=1
else
    if [[ $verbose == $(true) ]]; then
	echo -e "\tpylint was run with the --errors-only flag"
	echo -e "\tNo errors were found! Continuing..."
    fi
fi

##################################################

# unstash unstaged commits
# from https://codeinthehole.com/tips/tips-for-using-a-git-pre-commit-hook/
#STASHES=$(git stash list)
#if [[ $STASHES == *"$STASH_NAME" ]]; then
#    git stash pop --quiet
#fi

# check RESULT and exit based on it
if [[ $ERR -ne 0 ]]; then
    echo "-------------------------------------------"
    echo "    Pre-Commit Tests Found an Issue :(     "
    echo "-------------------------------------------"

    exit 1
fi

echo "-------------------------------------------"
echo "        Pre-Commit Tests Finished!         "
echo "-------------------------------------------"

exit 0

