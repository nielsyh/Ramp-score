# RAMP-SCORE

RAMP-SCORE is a Python implementation of the ramp-score used in solar forecasting. This implementation is based on the paper 'Towards a standardized procedure to assess solar forecast accuracy: A new ramp and time alignment metric' by Vallence et al. (2017).

## Usage:
```python
from ramp_score import get_ramp_score

ref_ls = [10, 11, 12, 30, 41, 42, 22, 10, 10]
model_ls = [10, 11, 12, 22, 41, 42, 22, 10, 10]
get_ramp_score("Title", 
                ref_ls, 
                model_ls, 
                avg_mins=60, 
                sens=80, 
                name='name', 
                plot=True)
