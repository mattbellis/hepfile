Use this to see what is in the directories and not in the repo.
This can produce errors with `flit publish`

```
git ls-files --deleted --others --exclude-standard
```
