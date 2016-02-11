#!/bin/sh

BLOG_HTTPDOCS="/usr/local/www/blog/httpdocs"
GIT_BIN="/usr/local/bin/git"
PELICAN_GIT="/usr/local/git/gufi-blog"
PELICAN_BIN="/usr/local/bin/pelican"

FOS=$(/usr/bin/uname -s | tr "[A-Z]" "[a-z]")
if [ ${FOS} != 'freebsd' ]; then
  echo "Is this a joke?"
  exit 1
fi

WHOAMI=$(/usr/bin/id -u)
if [ ${WHOAMI} -ne 0 ]; then
  echo "You are not root. There must be a reason."
  exit 1
fi

${GIT_BIN} -C ${PELICAN_GIT} pull
if [ $? -ne 0 ]; then
  echo "git exited with an error."
  exit 1
fi

${PELICAN_BIN} ${PELICAN_GIT}/content -s ${PELICAN_GIT}/publishconf.py -o ${BLOG_HTTPDOCS}
if [ $? -ne 0 ]; then
  echo "pelican exited with an error."
  exit 1
fi

exit 0
