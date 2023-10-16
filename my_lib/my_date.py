from datetime import date, timedelta, datetime


class DateHandler:
    
    
    def __init__(self, date_obj: date | datetime ) -> None:
        self.date_obj = date_obj
    
    @property
    def date_obj(self) -> date:
        return self._date_obj
    
    @date_obj.setter
    def date_obj(self, date_obj) -> None:
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        if not isinstance(date_obj, date):
            raise ValueError("Invalid date object. DateHandler requires a date or datetime object.")
        self._date_obj = date_obj
    
    def get_delta_days(self, input_days: int, max_delta: int = -10) -> 'DateHandler':
        if not (0 <= abs(input_days) <= abs(max_delta)):
            raise ValueError(f"Input days '{input_days}' must be a positive integer less than max delta '{max_delta}'.")
        
        self.date_delta = self.date_obj + timedelta(days=input_days)
        return self.__class__(self.date_delta)
    
    def formated_date(self, format='%d.%m.%Y' ) -> str:
        return self.date_obj.strftime(format)
 
 
if __name__ == "__main__":
    pass       


        
              