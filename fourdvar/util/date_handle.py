
import datetime as dt

import _get_root

#map string tags to date conversion functions
tag_map = {
    '<YYYYMMDD>': lambda date: date.strftime( '%Y%m%d' ),
    '<YYYYDDD>': lambda date: date.strftime( '%Y%j' ),
    '<YESTERDAY>': lambda date: ( date - dt.timedelta(days=1) ).strftime( '%Y%m%d' ),
    '<TOMORROW>': lambda date: ( date + dt.timedelta(days=1) ).strftime( '%Y%m%d' )
}

def replace_date( src, date ):
    """
    extension: replace date tags with date data
    input: string, date representation
    output: string
    
    notes: date can be a datetime.date, datetime.datetime or a [year,month,day]
    """
    #force date into type dt.date
    if isinstance( date, dt.date ):
        pass
    elif isinstance( date, dt.datetime ):
        date = date.date()
    else:
        date = dt.date( date[0], date[1], date[2] )
    
    #replace all date tags
    for tag in tag_map.keys():
        if tag in src:
            src = src.replace( tag, tag_map[ tag ]( date ) )
    return src
