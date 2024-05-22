from datetime import datetime
from datetime import datetime, timedelta
import pytz

def get_day_of_week(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    
    # Get the day of the week as an integer (0=Monday, 6=Sunday)
    day_of_week_number = date_obj.weekday()
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week_name = days_of_week[day_of_week_number]
    months_of_year = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
    month_name = months_of_year[date_obj.month - 1]

    # Return the month, date, and day of the week in a tuple
    return [month_name, date_obj.day, day_of_week_name]

def get_next_weekday(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    
    # If today is Friday (4), Saturday (5), or Sunday (6), add days to get to Monday (0)
    if date_obj.weekday() >= 4:  
        days_until_monday = 7 - date_obj.weekday()
        next_weekday = date_obj + timedelta(days=days_until_monday)
    else:
        next_weekday = date_obj + timedelta(days=1)
    
    return next_weekday

def get_upload_date(date):
    pst = pytz.timezone('America/Los_Angeles')
    next_weekday = get_next_weekday(date)
    
    # Set the time to 5 AM PST
    upload_datetime = next_weekday.replace(hour=5, minute=0, second=0, microsecond=0)
    
    # Localize to PST
    upload_datetime_pst = pst.localize(upload_datetime)
    
    # Convert to Unix timestamp
    unix_time = int(upload_datetime_pst.timestamp())
    month_name, day, day_of_week_name = get_day_of_week(upload_datetime_pst.strftime('%Y-%m-%d'))
    
    return month_name, day, day_of_week_name, unix_time

def spanish_title_case(text):
    # Words to keep in lowercase unless they are the first word
    lowercase_words = ['de', 'a', 'en', 'y', 'o', 'u', 'del', 'la', 'los', 'las', 'el', 'un', 'una', 'unos', 'unas']
    words = text.split()
    new_title = []
    for i, word in enumerate(words):
        if word.lower() in lowercase_words and i != 0:
            new_title.append(word.lower())
        else:
            new_title.append(word.capitalize())
    return ' '.join(new_title)

def english_title_case(text):
    # Words to keep in lowercase unless they are the first word
    lowercase_words = ['a', 'an', 'the', 'and', 'or', 'but', 'nor', 'at', 'by', 'for', 'from', 'in', 'into', 'near', 'of', 'on', 'onto', 'to', 'with']
    words = text.split()
    new_title = []
    for i, word in enumerate(words):
        if word.lower() in lowercase_words and i != 0:
            new_title.append(word.lower())
        else:
            new_title.append(word.capitalize())
    return ' '.join(new_title)