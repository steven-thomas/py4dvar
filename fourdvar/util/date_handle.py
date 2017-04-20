
import datetime as dt

import _get_root
import fourdvar.params.date_defn as defn

start_date = dt.datetime.strptime( str( defn.start_date ), '%Y%m%d' ).date()
end_date = dt.datetime.strptime( str( defn.end_date ), '%Y%m%d' ).date()

#map string tags to date conversion functions
tag_map = {
    '<YYYYMMDD>': lambda date: date.strftime( '%Y%m%d' ),
    '<YYYYDDD>': lambda date: date.strftime( '%Y%j' ),
    '<YESTERDAY>': lambda date: ( date - dt.timedelta(days=1) ).strftime( '%Y%m%d' ),
    '<TOMORROW>': lambda date: ( date + dt.timedelta(days=1) ).strftime( '%Y%m%d' )
}

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
