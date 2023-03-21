""" Wavelet utils """
import pywt

def dwt_coeffs(signal, name_mother_wavelet = 'db1', level = 4, type_coeff = 'lp'):

    mother_wavelet = pywt.Wavelet(name_mother_wavelet)

    if (type_coeff == 'lp'):
        cA = list()
        for i in range(1, level + 1):
            coefficients = pywt.downcoef('a', signal, mother_wavelet, mode = 'periodic', level = i)
            cA.append(coefficients[:int(len(signal)/(2 ** i))])
        return cA
    elif (type_coeff == 'hp'):
        cD = list()
        for i in range(1, level + 1):
            coefficients = pywt.downcoef('d', signal, mother_wavelet, mode = 'periodic', level = i)
            coefficients = coefficients * -1.
            cD.append(coefficients[:int(len(signal)/(2 ** i))])
        return cD
    else:
        print( "Wrong type coefficient. Choose between lp or hp.")
        return list()