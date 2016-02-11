#!/bin/sh

BLOG_HTTPDOCS="/usr/local/www/blog/httpdocs"
GIT_BIN="/usr/local/bin/git"
PELICAN_GIT="/usr/local/git/gufi-blog"
PELICAN_BIN="/usr/local/bin/pelican"

WHOAMI=$(id -u)

if [ ${WHOAMI} -ne 0 ]; then
  echo "You are not root. There must be a reason."
  exit 1
fi

${GIT_BIN} -C ${PELICAN_GIT} pull

${PELICAN_BIN} ${PELICAN_GIT}/content -s ${PELICAN_GIT}/publishconf.py -o ${BLOG_HTTPDOCS}
cd -

exit 0
