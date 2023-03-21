""" Wavelet utils """
import pywt
import numpy as np

def extract_dwt_coeffs(signal, name_mother_wavelet = 'haar', level = 4, type_coeff = 'lp'):

    mother_wavelet = pywt.Wavelet(name_mother_wavelet)

    cA = list()
    cD = list()

    dwt_lp_coeff_list = list()
    dwt_hp_coeff_list = list()

    if (type_coeff == 'lp'):
        # print("signal")
        # print (signal)
        for i in range(1, level + 1):
            coefficients = pywt.downcoef('a', signal, mother_wavelet, mode = 'periodic', level = i)
            # coefficients = coefficients * (0.7071067812 ** (i*2))
            cA.append(coefficients)
            # print("level"+str(i))
            # print(coefficients)
        dwt_lp_coeff_list = cA
        return dwt_lp_coeff_list
    elif (type_coeff == 'hp'):
        for i in range(1, level + 1):
            coefficients = pywt.downcoef('d', signal, mother_wavelet, mode = 'periodic', level = i)
            # coefficients = coefficients * (0.7071067812 ** (i*2)) * -1.
            coefficients = coefficients * -1.
            cD.append(coefficients)
        dwt_hp_coeff_list = cD
        return dwt_hp_coeff_list