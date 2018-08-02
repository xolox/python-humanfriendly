#!/bin/bash -e

# Even though Travis CI supports Mac OS X [1] and several Python interpreters
# are installed out of the box, the Python environment cannot be configured in
# the Travis CI build configuration [2].
#
# As a workaround the build configuration file specifies a single Mac OS X job
# with `language: generic' that runs this script to create and activate a
# Python virtual environment.
#
# Recently the `virtualenv' command seems to no longer come pre-installed on
# the MacOS workers of Travis CI [3] so when this situation is detected we
# install it ourselves.
#
# [1] https://github.com/travis-ci/travis-ci/issues/216
# [2] https://github.com/travis-ci/travis-ci/issues/2312
# [3] https://travis-ci.org/xolox/python-humanfriendly/jobs/411396506

if [ "$TRAVIS_OS_NAME" = osx ]; then
  VIRTUAL_ENV="$HOME/virtualenv/python2.7"
  if [ ! -x "$VIRTUAL_ENV/bin/python" ]; then
    if ! which virtualenv &>/dev/null; then
      # Install `virtualenv' in ~/.local (doesn't require `sudo' privileges).
      pip install --user virtualenv
      # Make sure ~/.local/bin is in the $PATH.
      LOCAL_BINARIES=$(python -c 'import os, site; print(os.path.join(site.USER_BASE, "bin"))')
      export PATH="$PATH:$LOCAL_BINARIES"
    fi
    virtualenv "$VIRTUAL_ENV"
  fi
  source "$VIRTUAL_ENV/bin/activate"
fi

eval "$@"
