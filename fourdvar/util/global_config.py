
import _get_root
import datetime as dt

#constants used in calculations:
#molar weight of dry air (precision matches cmaq
mwair = 28.9628 #g/mol
#convert proportion to ppm
ppm_scale = 1E6 #unitless
#convert g to kg
kg_scale = 1E-3 #kg/g

#note: every day in model starts at midnight (000000) and runs for 24 hours

start_date = None
end_date = None

def get_datelist():
    global start_date
    global end_date
    if start_date is None or end_date is None:
        raise ValueError( 'Need to define start_date and end_date.' )
    days = (end_date - start_date).days + 1
    datelist = [ start_date + dt.timedelta(days=i) for i in range(days) ]
    return datelist
