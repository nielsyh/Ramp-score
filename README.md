# RAMP-SCORE

RAMP-SCORE is a python implementation of the ramp-score used in solar forecasting. This implementation is based on the paper 'Towards a standardized procedure to assess solar forecast accuracy: A new ramp and time alignment metric' by Vallence et al. (2017).

## Usage:
 
get_ramp_score(ref_ls, model_ls, avg_mins=60, sens = 80, name='Compete', plot=True)
### Input: 
- Forecast reference list (list of observed values)

- Forecast model list (list of predicted values)

- Minutes to average on (positive integer, default = 60)

- Sensitivity, the sensitivity to calculate the slopes in the SD algorithm.

- Names of model.

- Plot, boolean if you want to plot output SD algorithm.

### Ouput:
- rampscore (positive float).
