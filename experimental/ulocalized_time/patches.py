# -*- coding: utf-8 -*-

import logging

from zope.i18n import translate
from zope.i18n.locales import locales

from Acquisition import aq_acquire
from DateTime.interfaces import IDateTime
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.log import log
from Products.CMFPlone.utils import safe_unicode

from Products.CMFPlone.i18nl10n import _interp_regex, datetime_formatvariables, name_formatvariables

from Products.CMFPlone.i18nl10n import weekdayname_msgid_abbr, weekdayname_msgid
from Products.CMFPlone.i18nl10n import monthname_msgid_abbr, monthname_msgid

def i18nl10n_ulocalized_time(time, long_format=None, time_only=None, context=None,
                             domain='plonelocales', request=None):
    """This patched version change the behaviour and the meaning of long_format parameter.

    This trick is quite ugly, but is the only way to keep compatibility with basic use case of this method
    all around Plone code.
    
    The format must be given using the .po format, so not if for example you want to translate this:
        '%a %d %b %Y'
    you need to change it to:
        '${a} ${d} ${b} ${Y}'
    """
    
    # get msgid
    if not long_format or (type(long_format)!=str and type(long_format)!=unicode):
        msgid = long_format and 'date_format_long' or 'date_format_short'
        if time_only is not None:
            msgid = 'time_format'
    else:
        msgid = long_format

    # NOTE: this requires the presence of three msgids inside the translation catalog
    #       date_format_long, date_format_short, and time_format
    #       These msgids are translated using interpolation.
    #       The variables used here are the same as used in the strftime formating.
    #       Supported are %A, %a, %B, %b, %H, %I, %m, %d, %M, %p, %S, %Y, %y, %Z, each used as
    #       variable in the msgstr without the %.
    #       For example: "${A} ${d}. ${B} ${Y}, ${H}:${M} ${Z}"
    #       Each language dependend part is translated itself as well.

    # From http://docs.python.org/lib/module-time.html
    #
    # %a    Locale's abbreviated weekday name.      
    # %A     Locale's full weekday name.     
    # %b     Locale's abbreviated month name.     
    # %B     Locale's full month name.     
    # %d     Day of the month as a decimal number [01,31].     
    # %H     Hour (24-hour clock) as a decimal number [00,23].     
    # %I     Hour (12-hour clock) as a decimal number [01,12].     
    # %m     Month as a decimal number [01,12].     
    # %M     Minute as a decimal number [00,59].     
    # %p     Locale's equivalent of either AM or PM.     
    # %S     Second as a decimal number [00,61].     
    # %y     Year without century as a decimal number [00,99].     
    # %Y     Year with century as a decimal number.     
    # %Z     Time zone name (no characters if no time zone exists).     

    mapping = {}
    # convert to DateTime instances. Either a date string or 
    # a DateTime instance needs to be passed.
    if not IDateTime.providedBy(time):
        try:
            time = DateTime(time)
        except:
            log('Failed to convert %s to a DateTime object' % time,
                severity=logging.DEBUG)
            return None

    if context is None:
        # when without context, we cannot do very much.
        return time.ISO()

    if request is None:
        request = aq_acquire(context, 'REQUEST')

    # get the formatstring
    formatstring = translate(msgid, domain, mapping, request)

    if formatstring is None or formatstring.startswith('date_') or formatstring.startswith('time_'):
        # msg catalog was not able to translate this msgids
        # use default setting

        properties=getToolByName(context, 'portal_properties').site_properties
        if long_format:
            format=properties.localLongTimeFormat
        else:
            if time_only:
                format=properties.localTimeOnlyFormat
            else:
                format=properties.localTimeFormat

        return time.strftime(format)
    
    # get the format elements used in the formatstring
    formatelements = _interp_regex.findall(formatstring)
    # reformat the ${foo} to foo
    formatelements = [el[2:-1] for el in formatelements]

    # add used elements to mapping
    elements = [e for e in formatelements if e in datetime_formatvariables]

    # add weekday name, abbr. weekday name, month name, abbr month name
    week_included = True
    month_included = True

    name_elements = [e for e in formatelements if e in name_formatvariables]
    if not ('a' in name_elements or 'A' in name_elements):
        week_included = False
    if not ('b' in name_elements or 'B' in name_elements):
        month_included = False

    for key in elements:
        mapping[key]=time.strftime('%'+key)

    if week_included:
        weekday = int(time.strftime('%w')) # weekday, sunday = 0
        if 'a' in name_elements:
            mapping['a']=weekdayname_msgid_abbr(weekday)
        if 'A' in name_elements:
            mapping['A']=weekdayname_msgid(weekday)
    if month_included:
        monthday = int(time.strftime('%m')) # month, january = 1
        if 'b' in name_elements:
            mapping['b']=monthname_msgid_abbr(monthday)
        if 'B' in name_elements:
            mapping['B']=monthname_msgid(monthday)

    # translate translateable elements
    for key in name_elements:
        mapping[key] = translate(mapping[key], domain, context=request, default=mapping[key])

    # translate the time string
    return translate(msgid, domain, mapping, request)

def ulocalized_time(self, time, long_format=None, time_only = None, context=None,
                    domain='plonelocales', request=None):
    # get some context if none is passed
    if context is None:
        context = self
    return i18nl10n_ulocalized_time(time, long_format, time_only, context, domain, request)

