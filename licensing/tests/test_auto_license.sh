#!/usr/bin/env bash

#
# These tests aren't perfect, but good enough for now without setting up pytest
#

[ "$DEBUG" = "1" ] && set -x

SCRIPTDIR="$(readlink -f "$(dirname "$0")")"
RESOURCESDIR="$SCRIPTDIR/resources/"

# If testing if the script respects existing LICENSE files, make a new test_repoX directory or modify/remove the
# `find` command below in this file.
REPODIR="$RESOURCESDIR/test_repo1"

mkdir "$REPODIR/.git" || exit 1

FAIL=0
if python3 "$SCRIPTDIR/../auto_license.py" "$REPODIR" 2>/dev/null; then
  printf "[!] TEST: Script failed to fail when project name not given\n" >&2
  FAIL=1
fi
if ! python3 "$SCRIPTDIR/../auto_license.py" "$REPODIR" -p YEE; then
  printf "[!] TEST: Script failed to succeed when it should have\n" >&2
  FAIL=1
fi

rmdir "$REPODIR/.git" || exit 1

if python3 "$SCRIPTDIR/../auto_license.py" "$REPODIR" -p YEE; then
  printf "[!] TEST: Script failed to fail when .git didn't exist\n" >&2
fi
if ! python3 "$SCRIPTDIR/../auto_license.py" "$REPODIR" -p YEE --no-git; then
  printf "[!] TEST: Script failed to respect --no-git flag\n" >&2
fi

find "$REPODIR" -type f -name "LICENSE*" -delete
git checkout -- "$RESOURCESDIR" >/dev/null

# New repo dir
REPODIR="$RESOURCESDIR/test_repo2"

if ! python3 "$SCRIPTDIR/../auto_license.py" "$REPODIR" -p YEE --no-git; then
  printf "[!] TEST: Script failed to succeed when it should have\n" >&2
  FAIL=1
fi

if [ "$FAIL" = "0" ]; then
  printf "[+] TEST: All tests passed!\n"
else
  printf "[!] TEST: Some tests did not pass\n"
fi

exit "$FAIL"
