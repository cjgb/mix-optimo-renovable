import pandas as pd
import numpy as np
from scipy.optimize import minimize

dat = pd.read_csv('data/ree.csv').sort_values('ts')
dat = dat.drop(['cc', 'car', 'gf', 'inter', 'icb', 'solFot', 'solTer', 'aut'], axis = 1)
dat['otra_renovable'] = dat.hid + dat.termRenov + dat.cogenResto
dat = dat.drop(['hid', 'termRenov', 'cogenResto'], axis = 1).copy()

num_dias = pd.to_datetime(dat.ts, errors = 'coerce').dt.date.value_counts().shape

def generacion_estimada(x):
    x1, x2, x3 = x
    out = x1 * dat.eol + x2 * dat.sol + x3 * dat.nuc + dat.otra_renovable
    return out

# se guarda en MW durante 5 minutos (12 veces más que MWh)
# porque los datos son cincominutales y operamos en potencias
# (una potencia de 1000 MW durante 5 minutos consume 1000 / 12 MWh)
# usamos la misma capacidad que
# https://twitter.com/victorgcBCN/status/1560693777123377152
ALMACENAMIENTO_MAXIMO = 20000 * 4 * 12
ALMACENAMIENTO_INICIAL = ALMACENAMIENTO_MAXIMO / 2.0

def perdida_asimetrica(x, verbose = False):
    y  = dat.dem.to_numpy()
    yh = generacion_estimada(x).to_numpy()

    desaprovechada = np.zeros(y.shape)
    almacenada = np.zeros(y.shape)
    almacenada[0] = ALMACENAMIENTO_INICIAL
    apagones = np.zeros(y.shape)

    # si se genera menos de la necesaria,
    # se tiene que tirar de almacenada
    deficit = (y - yh).clip(min = 0)
    exceso  = (yh - y).clip(min = 0)

    for i in range(1, len(y)):
        if deficit[i] > 0:
            almacenada[i] = almacenada [i-1] - deficit[i]
            if almacenada[i] < 0:
                apagones[i] = -almacenada[i]
                almacenada[i] = 0
        if exceso[i] > 0:
            almacenada[i] = almacenada [i-1] + exceso[i]
            if almacenada[i] > ALMACENAMIENTO_MAXIMO:
                desaprovechada[i] = almacenada[i] - ALMACENAMIENTO_MAXIMO
                almacenada[i] = ALMACENAMIENTO_MAXIMO

    apagones_total = sum(apagones)
    desaprovechada_total = sum(desaprovechada)

    if verbose:
        return (apagones, desaprovechada, almacenada)

    return apagones_total + desaprovechada_total / 1000.0


res_nuclear = minimize(perdida_asimetrica, (1,1, 1))
apagones, desaprovechada, almacenada = perdida_asimetrica(res_nuclear.x, verbose = True)

tmp = dat.copy()
tmp['apagones'] = apagones
tmp['desaprovechada'] = desaprovechada
tmp['almacenada'] = almacenada
tmp.to_csv('results/analisis-renovables-nuclear.csv')


