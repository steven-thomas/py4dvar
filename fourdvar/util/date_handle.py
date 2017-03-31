
import datetime as dt

import _get_root

start_date = None
end_date = None

#map string tags to date conversion functions
tag_map = {
    '<YYYYMMDD>': lambda date: date.strftime( '%Y%m%d' ),
    '<YYYYDDD>': lambda date: date.strftime( '%Y%j' ),
    '<YESTERDAY>': lambda date: ( date - dt.timedelta(days=1) ).strftime( '%Y%m%d' ),
    '<TOMORROW>': lambda date: ( date + dt.timedelta(days=1) ).strftime( '%Y%m%d' )
}

def set_start_date( arg, method='<YYYYMMDD>' ):
    """
    extension: set the start_date attribute globally
    input: arg_val, string
    output: None
    
    notes: can implement multiple methods of defining start_date
    method = '<YYYYDDD>':
        arg is YearJulianDay as a single integer (eg: 2007161)
    method = '<YYYYMMDD>':
        arg is YearMonthDay as a single integer (eg: 20070614)
    """
    global start_date
    
    if method == '<YYYYDDD>':
        arg = str( arg )
        arg_date = dt.datetime.strptime( arg, '%Y%j' ).date()
    elif method == '<YYYYMMDD>':
        arg = str( arg )
        arg_date = dt.datetime.strptime( arg, '%Y%m%d' ).date()
    else:
        raise ValueError( 'input method {} is not valid'.format( method ) )
    
    msg = 'cannot change start_date'
    assert start_date is None or arg_date == start_date, msg
    start_date = arg_date
    return None

def set_end_date( arg, method='<YYYYMMDD>' ):
    """
    extension: set the end_date attribute globally
    input: arg_val, string
    output: None
    
    notes: can implement multiple methods of defining start_date
    method = 'start+tsec':
        arg is integer No. seconds from start_date to end_date
    method = '<YYYYMMDD>':
        arg is YearMonthDay as a single integer (eg: 20070614)
    """
    global start_date
    global end_date
    
    if method == 'start+tsec':
        assert start_date is not None, 'Must define start_date first'
        arg = int( arg )
        arg_date = start_date + dt.timedelta( seconds=arg )
    elif method == '<YYYYMMDD>':
        arg = str( arg )
        arg_date = dt.datetime.strptime( arg, '%Y%m%d' ).date()
    else:
        raise ValueError( 'input method {} is not valid'.format( method ) )
    
    msg = 'cannot change end_date'
    assert end_date is None or arg_date == end_date, msg
    end_date = arg_date
    return None

def get_datelist():
    """
    extension: get the list of dates with model runs over
    input: None
    output: list of datetime.date objects
    
    notes: require start_date & end_date to already be defined
    """
    global start_date
    global end_date
    if start_date is None or end_date is None:
        raise ValueError( 'Need to define start_date and end_date.' )
    days = (end_date - start_date).days + 1
    datelist = [ start_date + dt.timedelta(days=i) for i in range(days) ]
    return datelist

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

def add_days( date, ndays ):
    """
    extension: return the date ndays after date
    input: datetime.date, int
    output: datetime.date
    """
    return date + dt.timedelta( days=ndays )
