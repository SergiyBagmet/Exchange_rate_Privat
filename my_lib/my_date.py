from datetime import date, timedelta
import typing as t

class DateDeltaDay:
    
    
    def __init__(self, date_obj: date, delta_d: int, max_delta: int=10, negative: bool=False) -> None:
        self.date_obj = date_obj
        self.date_delta_obj = self._set_date_delta(delta_d, max_delta, negative)
        
        self._delta_d = delta_d
        self._max_delta = max_delta
        self._negative = negative
    
    def _set_date_delta(self, input_days: int, max_delta, negative):
        if not 0 <= input_days <= max_delta:
            raise ValueError(f"Input days '{input_days}' must be a positive integer less than max delta '{max_delta}'.")
        input_days = input_days if not negative else -input_days
        return self.date_obj + timedelta(days=input_days)

    def get_min_max_date(self) -> list[date]:
        if self._delta_d == 0:
            return [self.date_obj]
        
        min_date, max_date = self.date_obj, self.date_delta_obj
        if self._negative:
            min_date, max_date = max_date, min_date
        
        return [min_date, max_date]
    
    def delta_days_generator(self, step_days: int=1) -> t.Generator[date, None, None]:     
        min_date, max_date = self.get_min_max_date()
        for i in range(0, self._delta_d, step_days):
            yield min_date + timedelta(days=i)
        yield max_date    

 
if __name__ == "__main__":
    pass
    # delta_5 = DateDeltaDay(date_obj=date.today(), delta_d=7, negative=True )
    # print(type(delta_5.get_min_max_date()))
    # print()
    # [print(date) for date in delta_5.delta_days_generator()]
    


        
              