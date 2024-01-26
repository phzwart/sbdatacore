from datetime import datetime, timedelta

def convert_mdy(date_str):
    """
    Converts a date from MMDDYY or MMDYY format to YYYY_MM_DD format.
    In case of ambiguity in the year, the date closest to today's date is chosen.

    Args:
    date_str (str): The date string in MMDDYY or MMDYY format.

    Returns:
    str: The date in YYYY_MM_DD format.
    """
    today = datetime.today()
    current_year = today.year

    # Function to parse date and find the year closest to current year
    def parse_date(month, day, year):
        year_option_1 = int("20" + year)
        year_option_2 = int("19" + year) if year_option_1 > current_year else int("21" + year)

        try:
            date_option_1 = datetime(year=year_option_1, month=int(month), day=int(day))
        except ValueError:
            date_option_1 = None

        try:
            date_option_2 = datetime(year=year_option_2, month=int(month), day=int(day))
        except ValueError:
            date_option_2 = None

        if date_option_1 and (not date_option_2 or abs(today - date_option_1) < abs(today - date_option_2)):
            return date_option_1
        elif date_option_2:
            return date_option_2
        else:
            raise ValueError("Invalid date")

    if len(date_str) == 6:  # MMDDYY
        month, day, year = date_str[:2], date_str[2:4], date_str[4:]
    elif len(date_str) == 5:  # MMDYY
        # Assuming first digit is month (M) and next two are day (DD)
        month, day, year = date_str[:1], date_str[1:3], date_str[3:]
    else:
        return "Invalid format"

    parsed_date = parse_date(month, day, year)
    return parsed_date.strftime("%Y_%m_%d")
