# causalml

## github 

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

### Switching Accounts

Git Credential Manager allows you to assign a specific user to each git repo. This allows us to have multiple repos on the same machine but different users committing to it. E.g. causalml is linked to `prichaudhuri` and SynthTest is `schattrg`. Set the repo to a specific user and then go to github.com and login/switch to your account and you will see the create PR banner.

#### Setting it up
As an example, let's say you're working on multiple repositories hosted at the same domain name.

Repo URL	Identity
https://example.com/open-source/library.git	contrib123
https://example.com/more-open-source/app.git	contrib123
https://example.com/big-company/secret-repo.git	employee9999
When you clone these repos, include the identity and an @ before the domain name in order to force Git and GCM to use different identities. If you've already cloned the repos, you can update the remote URL to include the identity.

#### Example: fresh clones

```
# instead of `git clone https://example.com/open-source/library.git`, run:
git clone https://contrib123@example.com/open-source/library.git

# instead of `git clone https://example.com/big-company/secret-repo.git`, run:
git clone https://employee9999@example.com/big-company/secret-repo.git
```

#### Example: existing clones

```
# in the `library` repo, run:
git remote set-url origin https://contrib123@example.com/open-source/library.git

# in the `secret-repo` repo, run:
git remote set-url origin https://employee9999@example.com/big-company/secret-repo.git
```

