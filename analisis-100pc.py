import pandas as pd
import numpy as np
from scipy.optimize import minimize

dat = pd.read_csv('data/ree.csv').sort_values('ts')
dat = dat.drop(['nuc', 'cc', 'car', 'gf', 'inter', 'icb', 'solFot', 'solTer', 'aut'], axis = 1)
dat['otra_renovable'] = dat.hid + dat.termRenov + dat.cogenResto
dat = dat.drop(['hid', 'termRenov', 'cogenResto'], axis = 1).copy()

num_dias = pd.to_datetime(dat.ts, errors = 'coerce').dt.date.value_counts().shape

def generacion_estimada(x1, x2):
    out = x1 * dat.eol + x2 * dat.sol + dat.otra_renovable
    return out

def perdida_rmse(x):
    x1, x2 = x
    tmp = dat.dem - generacion_estimada(x1, x2)
    tmp = np.sqrt((tmp**2).mean())
    return tmp

res_rmse = minimize(perdida_rmse, (1,1))


# se guarda en MW durante 5 minutos (12 veces más que MWh)
# porque los datos son cincominutales y operamos en potencias
# (una potencia de 1000 MW durante 5 minutos consume 1000 / 12 MWh)
# usamos la misma capacidad que
# https://twitter.com/victorgcBCN/status/1560693777123377152
ALMACENAMIENTO_MAXIMO = 20000 * 4 * 12
ALMACENAMIENTO_INICIAL = ALMACENAMIENTO_MAXIMO / 2.0

def perdida_asimetrica(x, verbose = False):
    x1, x2 = x
    y  = dat.dem.to_numpy()
    yh = generacion_estimada(x1, x2).to_numpy()

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

    print((x, (apagones_total + desaprovechada_total / 1000.0) / 1e6))

    if verbose:
        return (apagones, desaprovechada, almacenada)

    return apagones_total + desaprovechada_total / 1000.0


res_asimetrico = minimize(perdida_asimetrica, (1,1))
apagones, desaprovechada, almacenada = perdida_asimetrica(res_asimetrico.x, verbose = True)

tmp = dat.copy()
tmp['apagones'] = apagones
tmp['desaprovechada'] = desaprovechada
tmp['almacenada'] = almacenada
tmp.to_csv('results/apagones.csv')
tmp[tmp.apagones > 0].to_csv('/tmp/apagones.csv')



# cálculo del almacenamiento necesario para poder
# utilizar el óptimo RMSE

ALMACENAMIENTO_MAXIMO = 20000 * 4 * 12
ALMACENAMIENTO_INICIAL = ALMACENAMIENTO_MAXIMO / 2.0
ALMACENAMIENTO_MAXIMO = 1e12

apagones, desaprovechada, almacenada = perdida_asimetrica(res_rmse.x, verbose = True)

tmp = dat.copy()
tmp['almacenada'] = almacenada
tmp.to_csv('results/almacenada.csv')