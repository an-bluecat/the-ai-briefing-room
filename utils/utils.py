from datetime import datetime
from datetime import datetime, timedelta
import pytz
from PIL import Image
import os


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


def compress_image_to_target_size(input_path, target_size_mb, initial_quality=85, step=5):
    """
    Compresses an image to ensure its size is below a target size in MB, overwriting the original image.

    :param input_path: Path to the input image.
    :param target_size_mb: Target size in MB.
    :param initial_quality: Initial quality for compression.
    :param step: Step to reduce quality in each iteration.
    """
    target_size_bytes = target_size_mb * 1024 * 1024
    quality = initial_quality

    with Image.open(input_path) as img:
        while True:
            img.save(input_path, 'JPEG', quality=quality)
            output_size = os.path.getsize(input_path)
            
            if output_size <= target_size_bytes or quality <= step:
                break

            quality -= step
            if quality <= 0:
                raise ValueError("Cannot compress image to the desired size.")
