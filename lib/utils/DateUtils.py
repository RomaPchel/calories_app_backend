from datetime import date, datetime
from typing import Optional, Tuple

from fastapi import HTTPException


def get_dates(day):
    try:
        target_date = date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD'.")

        # Calculate start and end of the day
    start_of_day = datetime.combine(target_date, datetime.min.time())  # 00:00:00 of the target date
    end_of_day = datetime.combine(target_date, datetime.max.time())  # 23:59:59 of the target date

    return start_of_day, end_of_day


def parse_dates(start_date: Optional[str], end_date: Optional[str]) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
    start_of_day = None
    end_of_day = None

    # If start_date is provided, parse it into a date object
    if start_date:
        try:
            start_of_day = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid start date format: {start_date}. Use 'YYYY-MM-DD'.")

    # If end_date is provided, parse it into a date object
    if end_date:
        try:
            end_of_day = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid end date format: {end_date}. Use 'YYYY-MM-DD'.")

    return start_of_day, end_of_day
