"""
date_handle.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import datetime as dt

import fourdvar.params.date_defn as defn

start_date = dt.datetime.strptime( str( defn.start_date ), '%Y%m%d' ).date()
end_date = dt.datetime.strptime( str( defn.end_date ), '%Y%m%d' ).date()

#map string tags to date conversion functions
tag_map = {
    '<YYYYMMDD>': lambda date: date.strftime( '%Y%m%d' ),
    '<YYYYDDD>': lambda date: date.strftime( '%Y%j' ),
    '<YYYY-MM-DD>': lambda date: date.strftime( '%Y-%m-%d' )
}

def add_days( date, ndays ):
    """
    extension: return the the date ndays before/after date
    input: datetime.date, int (-ve for bwd in time)
    output: datetime.date
    """
    return date + dt.timedelta( days=ndays )

def get_datelist():
    """
    extension: get the list of dates which the model runs over
    input: None
    output: list of datetime.date objects
    
    notes: require start_date & end_date to already be defined
    """
    global start_date
    global end_date
    if start_date is None or end_date is None:
        raise ValueError( 'Need to define start_date and end_date.' )
    days = (end_date - start_date).days + 1
    datelist = [ add_days( start_date, i ) for i in range(days) ]
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
        mtag = tag[:-1] + '#'
        while mtag in src:
            tstart = src.index( mtag ) + len(mtag)
            tend = src.index( '>', tstart )
            ndays = int( src[tstart:tend] )
            mdate = add_days( date, ndays )
            src = src[:tstart-1] + src[tend:]
            src = src.replace( tag, tag_map[ tag ](mdate) )
    return src

def move_tag( src_str, ndays ):
    """
    extension: add a day modifier to a date tag
    input: string, integer
    output: string
    """
    modifier = '{:+}'.format( int(ndays) )
    for tag in tag_map.keys():
        if tag in src_str:
            new_tag = '<{}#{}>'.format( tag[1:-1], modifier )
            src_str = src_str.replace( tag, new_tag )
    return src_str

def reset_tag( src_str ):
    """
    extension: undo move_tag day modifier
    input: string
    output: string
    """
    for tag in tag_map.keys():
        mtag = tag[:-1] + '#'
        while mtag in src_str:
            tstart = src_str.index( mtag ) + len(mtag)
            tend = src_str.index( '>', tstart )
            src_str = src_str[:tstart-1] + src_str[tend:]
    return src_str
