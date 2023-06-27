#!/bin/bash

verbose=true

if [[ $verbose = true ]]; then
    echo "-------------------------------------------"
    echo "        Beginning Pre-Commit Tests         "
    echo "-------------------------------------------"
fi
# stash unstaged commits
# recommended by: https://codeinthehole.com/tips/tips-for-using-a-git-pre-commit-hook/
# STASH_NAME="pre-commit-$(date +%s)"
# git stash save --quiet --keep-index --include-untracked $STASH_NAME

##################################################
# Run tests
##################################################
# run pytest and give exit code 1 if not successful

if [[ $verbose = true ]]; then
    echo "1) Running Python Unit Tests"
    python tests/runtests.py --verbose 
else
    python tests/runtests.py 1>/dev/null
fi
ERR=$?

if [[ $verbose = true ]]; then
    echo -e "\tPython tests finished with exit code $ERR"
fi

##################################################
# check for debug statements (we don't want these clogging our code)
if [[ $ERR == 0 ]]; then
    [ $verbose = true ] && echo -e "\n"

    if [[ $verbose = true ]]; then
	    echo "2) Checking for superfluous debug statements"
    fi

    GREP_RESULT=$(grep "pdb" src/hepfile/*.py | tr "\n" "|" | sed s/"|"/"\n\t"/)
    if [[ $GREP_RESULT ]]; then
	    if [[ $verbose = true ]]; then
	      echo -e "\tFound a pdb statement:" 
	      echo -e "\t$GREP_RESULT"
	    fi	 
	    ERR=1
    else
	    [ $verbose = true ] && echo -e "\tNo debug statements found! Continuing..."
    fi
fi
##################################################
# run black code formatter
if [[ $ERR == 0 ]]; then
    [ $verbose = true ] && echo -e "\n"

    BLACK_RESULT="$(black --target-version=py37 ./src/hepfile/*.py 2>&1)"
    if [[ $verbose = true ]]; then
	echo "3) Running black"
	echo -e "\t$BLACK_RESULT" | tr "\n" "*" | sed s/\*/"\n\t"/    
    fi

    if [[ $(grep "reformatted" <<< $BLACK_RESULT) ]]; then
	echo -e "\n\tBlack was run and reformatted code"
	echo -e "\tPlease add new changes using 'git add' before continuing"
	ERR=1 
    fi
fi
    
##################################################
# run pylint to give a warning if stuff doesn't look right
if [[ $ERR == 0 ]]; then 
    [ $verbose = true ] && echo -e "\n"

    if [[ $verbose = true ]]; then
	echo "4) Running pylint"
    fi
    
    PYLINT_RESULT=$(pylint hepfile | tr "\n" "|" | sed s/"|"/"\n\t"/)
    if [[ $PYLINT_RESULT ]]; then
	if [[ $verbose = true ]]; then
	    echo -e "\tWARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	    echo -e "\tpylint found some possible errors!"
	    echo -e "\tCommit will continue, but be cautious!"
	    echo -e "\tPlease check the following pushing:"
	    echo -e "\t$PYLINT_RESULT"
	fi
	#ERR=1
    else

	if [[ $verbose = true ]]; then
	    echo -e "\tpylint was run with the --errors-only flag"
	    echo -e "\tNo errors were found! Continuing..."
	fi
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
[ verbose = true ] && echo -e "\n"

if [[ $ERR -ne 0 ]]; then
    if [[ verbose = true ]]; then
	echo "-------------------------------------------"
	echo "    Pre-Commit Tests Found an Issue :(     "
	echo "-------------------------------------------"
    fi
    
    exit 1
fi

if [[ verbose = true ]]; then
    echo "-------------------------------------------"
    echo "        Pre-Commit Tests Finished!         "
    echo "-------------------------------------------"
fi

exit 0

