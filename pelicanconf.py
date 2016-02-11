#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u"Gruppo Utenti FreeBSD Italia"
SITENAME = u'GUFI Blog'
SITEURL = ''

PATH = 'content'
STATIC_PATHS = ['images', 'pdf']

TIMEZONE = 'Europe/Rome'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None 
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
        ('Sito GUFI', 'http://www.gufi.org'),
        ('FreeBSD', 'http://www.freebsd.org'),
        )

# Social widget
SOCIAL = (
        ('Twitter', 'https://twitter.com/freebsd_it'),
        ('Facebook', 'https://facebook.com/'),
        ('LinkedIN', 'https://it.linkedin.com/in/GUFI'),
        )   

THEME = "/usr/local/www/pelican-themes/pelican-themes/pelican-bootstrap3/"

DEFAULT_PAGINATION = 5

TWITTER_USERNAME = "freebsd_it"

ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

YEAR_ARCHIVE_SAVE_AS = '{date:%Y}/index.html'
MONTH_ARCHIVE_SAVE_AS = '{date:%Y}/{date:%m}/index.html'


########  THEME SPECIFICS ########

#DISPLAY_BREADCRUMBS = "True"
#DISPLAY_CATEGORY_IN_BREADCRUMBS = "True"
DISPLAY_PAGES_ON_MENU = "True"
DISPLAY_CATEGORIES_ON_MENU = "True" 

BOOTSTRAP_NAVBAR_INVERSE = "True"

DISPLAY_TAGS_INLINE = "True"

ABOUT_ME = "We're the Italian FreeBSD Users Group!"
#AVATAR = "images/max.jpg"

TWITTER_USERNAME = "freebsd_it"
#TWITTER_WIDGET_ID = "675741800607457280"

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
