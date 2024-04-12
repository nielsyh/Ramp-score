import numpy as np
from matplotlib import pyplot as plt
from swinging_door import SwingingDoor
from typing import List


def calc_ramp_score(reference_x: List[float], reference_y: List[float], competing_x: List[float],
                    competing_y: List[float], avg_mins: int) -> float:
    """
    Calculate the ramp score.

    rs = 1/n Integral |SD ts - SD ref|

    :param reference_x: List of timestamps for the reference data
    :param reference_y: List of GHI values for the reference data
    :param competing_x: List of timestamps for the competing data
    :param competing_y: List of GHI values for the competing data
    :param avg_mins: Number of minutes to average over
    :return: Ramp score
    """
    t_min = reference_x[0]
    t_max = reference_x[-1]

    result = []
    for i in range(t_min, t_max, avg_mins):
        result.append(abs(np.trapz(y=competing_y[i:i + avg_mins], x=competing_x[i:i + avg_mins]) - np.trapz(
            y=reference_y[i:i + avg_mins], x=reference_x[i:i + avg_mins])))
    return (1 / (t_max - t_min)) * sum(result)


def get_ramp_score(title_y: str, ref_ls: List[float], model_ls: List[float], avg_mins: int = 60, sens: int = 80,
                   name: str = 'Compete', plot: bool = True) -> float:
    """
    Calculate the ramp score between reference and model data.

    :param title_y: Title of y axe
    :param ref_ls: List of reference data
    :param model_ls: List of model data
    :param avg_mins: Number of minutes to average over
    :param sens: Sensitivity for compression
    :param name: Name for the plot
    :param plot: Whether to plot the data
    :return: Ramp score
    """
    kwh_sens = sens
    kwh_sens = kwh_sens / 100

    swinging_door = SwingingDoor()
    y_reference, x_reference = swinging_door.compress(ref_ls, kwh_sens, avg_mins)
    y_compete, x_compete = swinging_door.compress(model_ls, kwh_sens, avg_mins)

    if plot:
        plt.plot(ref_ls, linestyle='-', color='gray', label='Actual')
        plt.plot(x_reference, y_reference, color='blue', linestyle=':', label='Ramp Observed')
        plt.plot(x_compete, y_compete, color='red', linestyle=':', label='Ramp Predicted')

        fz = 20
        plt.title('SwingDoor compression ' + str(name), fontsize=fz)
        plt.xlabel('Time in minutes', fontsize=fz)
        plt.ylabel(title_y, fontsize=fz)

        plt.legend()
        plt.show()
        plt.close()

    rs = calc_ramp_score(x_reference, y_reference, x_compete, y_compete, avg_mins)
    return rs
