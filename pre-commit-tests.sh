#!/bin/bash

verbose=$(true)

echo "-------------------------------------------"
echo "        Beginning Pre-Commit Tests         "
echo "-------------------------------------------"

# stash unstaged commits
# recommended by: https://codeinthehole.com/tips/tips-for-using-a-git-pre-commit-hook/
STASH_NAME="pre-commit-$(date +%s)"
git stash save --quiet --keep-index --include-untracked $STASH_NAME

##################################################
# Run tests
##################################################

# run pytest and give exit code 1 if not successful
python -m pytest > /dev/null 
ERR=$?
if [[ $verbose == $(true) ]]; then
    echo "1) Python Tests Finished (exit code $ERR)"
fi
    
# run linter

##################################################

# unstash unstaged commits
# from https://codeinthehole.com/tips/tips-for-using-a-git-pre-commit-hook/
STASHES=$(git stash list)
if [[ $STASHES == *"$STASH_NAME" ]]; then
    git stash pop --quiet
fi

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

