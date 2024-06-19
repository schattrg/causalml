# causalml

## github 
test
### Basic Workflow
update local main branch
```
git checkout main
git pull origin main
```
create a new branch
```
git checkout -b new_branch_name
```
git branch naming convention - 

```
feature/feature_name : f-featurename
bugfix/bug_name : b-bugname
exploratory/exploratory_name : e-exploratoryname
```

Do your work, when it is time to commit
```
git add .
git commit -m "message"
git push origin new_branch_name
```
Go to github and create a pull request and ask for review

### Conflicts
These happen when you are trying to merge your branch with the main branch and there are changes in the same file in both branches. So it's a good habit to update your local main branch before creating a new branch. If you have been working on your branch for long, it's a good idea to update your local main branch and merge it with your branch to avoid conflicts. If there are conflicts, you will have to resolve them manually before commiting the changes.

Before creating a PR -
```
git checkout main
git pull origin main
git checkout new_branch_name
git merge main
```
