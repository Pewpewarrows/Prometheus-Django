In-file comments, in order of importance
========================================

# FIXME:
# TODO:
# HACK:
# XXX:


General
=======

# shell.py script that works like Django's `manage.py shell`
# runserver.py for quickly spawning a dev server
# CI setup under script/


Notes
=====

* It would be nice to keep static/ under promdjango/, for very self-contained apps
* But, static/ should technically be kept outside...
* Foreman Procfiles
* Should include this at the top of all python files?...
    # -*- coding: utf-8 -*-
    # vim: set fileencoding=utf-8 :
    from __future__ import absolute_imports, division, unicode_literals
    # three gotchas: print u'' % encoded_str; for c in u'': ; and file ops:
    # import locale, codecs
    # lang, encoding = locale.getdefaultlocale()
    # codecs.open('blar.txt', 'w', encoding).write(u'')
