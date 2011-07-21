.. contents::

Introduction
============

This product can be used by people that want to use an `strftime compatible format`__ for display
locale sensible data inside Plone templates.

__ http://docs.python.org/library/time.html#time.strftime

The Python Way
--------------

Python support locales through the `locale module`__ but this seems not working properly inside Plone,
for example the `setlocale function`__ says:

    setlocale() is not thread-safe on most systems. Applications typically start with a call of
    
    >>> import locale
    >>> locale.setlocale(locale.LC_ALL, '')
    
    This sets the locale for all categories to the user’s default setting (typically specified in the
    LANG environment variable). If the locale is not changed thereafter, using multithreading should not
    cause problems.

__ http://docs.python.org/library/locale.html
__ http://docs.python.org/library/locale.html#locale.setlocale

So it seems that you can force a locale (or use the system ones) but I fear this is not a good idea for Plone
sites that need to be used in more than a language. Plone itself don't use the Python locales for translate dates
elements.

The Plone Way
-------------

Inside Plone you can print date in a full working i18n aware way using the ``toLocalizedTime`` method of the
``ploneview``. However you can simply use a couple of format: *long_format* or *short_format*, defined in the
Plone localization product, passing ``True`` or ``False`` as second parameter:

    >>> from DateTime import DateTime
    >>> t = DateTime()
    >>> ploneview.toLocalizedTime(t, True)

Alternative
===========

Installing this product will give you an alternative, patching Plone. You can continue using ``toLocalizedTime``
but you can play with the ``long_format`` parameter, that in fact became also a *format* parameter.

You can still use the method as above (so basic Plone features are not touched) but you can provide a
``long_format`` value that can be a format string.

For example, a valid Python date string format as "``%a %d hello guys %b %Y``" became
"``${a} ${d} hello guys ${b} ${Y}``", so:

    >>> from DateTime import DateTime
    >>> t = DateTime()
    >>> ploneview.toLocalizedTime(t, "${a} ${d} hello guys ${b} ${Y}")

Warning
-------

Maybe this product is wrong and there is a way to make strftime working properly in a Plone multi-language site,
but I don't find any information about an alternative way! If you know how to do this, please contribute
to `the discussion`__ and help me deprecate this add-on!

__ http://permalink.gmane.org/gmane.comp.web.zope.plone.user/114706

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
