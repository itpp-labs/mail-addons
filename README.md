# addons-dev

Addons Forge

# Initialization

1. Fork this repo
2. Clone to your machine:

        git clone git@github.com:USERNAME/addons-dev.git

3. Add remotes

        cd addons-dev

        git remote add upstream          git@github.com:yelizariev/addons-dev.git
        git remote add addons-yelizariev https://github.com/yelizariev/addons-yelizariev.git
        git remote add pos-addons        https://github.com/yelizariev/pos-addons.git
        git remote add mail-addons       https://github.com/yelizariev/mail-addons.git
        git remote add access-addons     https://github.com/yelizariev/access-addons.git
        git remote add website-addons    https://github.com/yelizariev/website-addons.git
        git remote add l10n-addons       https://github.com/yelizariev/l10n-addons.git

# New branch

    # specify target repo and branch:
    export REPO=addons-yelizariev BRANCH=9.0

    # fetch remote
    git fetch ${REPO}

    # create new branch
    git checkout -b ${REPO}-${BRANCH}-some-feature ${REPO}/${BRANCH}

    # develop addons, create commits
    # ...

    # push to upstream
    git push upstream addons-yelizariev-9.0-some-feature

# PR to existed branch

If branch (e.g. *addons-yelizariev-9.0-some-feature*) already exists, send commits to your fork first and then create PR to **addons-dev**

# Final PR to target repo

    # example for addons-yelizariev
    cd /path/to/addons-yelizariev

    # add remote if it doesn't exist yet
    git remote add addons-dev https://github.com/yelizariev/addons-dev.git

    # fetch remote
    git fetch addons-dev

    # create branch
    git checkout -b addons-dev/addons-yelizariev-9.0-some-feature

    # push to your fork of target repo
    git push origin addons-yelizariev-9.0-some-feature

    # create PR to target repo
