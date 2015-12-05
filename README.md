# addons-dev

Addons Forge

# Initialization

1. Fork this repo
2. Clone to your machine:

        git clone git@github.com:USERNAME/addons-dev.git

3. Add remotes

        cd addons-dev

        git remote add addons-yelizariev https://github.com/yelizariev/addons-yelizariev.git
        git remote add pos-addons        https://github.com/yelizariev/pos-addons.git
        git remote add mail-addons       https://github.com/yelizariev/mail-addons.git
        git remote add access-addons     https://github.com/yelizariev/access-addons.git
        git remote add website-addons    https://github.com/yelizariev/website-addons.git
        git remote add l10n-addons       https://github.com/yelizariev/l10n-addons.git

# Development

    # specify target repo and branch:
    export REPO=addons-yelizariev BRANCH=9.0

    # fetch remote
    git fetch ${REPO}

    # create new branch
    git checkout -b ${REPO}-${BRANCH}-some-feature

    # develop addons, create commits
    # ...

    # push to your fork
    git push origin addons-yelizariev-9.0-some-feature

    # create pull request at github to addons-dev repo
    # then PR is checked and merged
    # then your update is tested again
    # then clean addon is pull-requested to target repo
