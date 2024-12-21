from datetime import datetime

from fastapi import HTTPException


def get_dates(start_date, end_date):
    if start_date:
        try:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use 'YYYY-MM-DD'")
    else:
        parsed_start_date = None

    if end_date:
        try:
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use 'YYYY-MM-DD'")
    else:
        parsed_end_date = None

    return parsed_start_date, parsed_end_date