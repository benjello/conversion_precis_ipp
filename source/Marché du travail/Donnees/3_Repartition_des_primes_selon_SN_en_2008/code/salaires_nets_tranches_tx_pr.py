
from __future__ import division
import pandas as pd
import os
import numpy as np
import pandas
from pandas import DataFrame, Series
#import statsmodels.formula.api as sm
#from sklearn.linear_model import LinearRegression
import scipy, scipy.stats
from scipy.integrate import simps
# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import seaborn as sns


file_path = "C:/Users/lisa.degalle/desktop/"

data_2008 = pd.read_excel(os.path.join(file_path, 'FPE_2008.xls'), sheetname = 2)
data_2002 = pd.read_excel(os.path.join(file_path, 'FPE_2002.xls'), sheetname = 1)
data_2005 = pd.read_excel(os.path.join(file_path, 'FPE_2005.xls'), sheetname = 1)

fig = plt.figure()

ax = fig.add_subplot(111)
fig.subplots_adjust(top=0.85)

ax.set_xlabel('part cumulee des agents tries de la plus basse tranche de taux de prime a la plus elevee')
ax.set_ylabel('part cumulee des primes recues')


def plot_cout_primes_tranche_salaire(data, annee):
    data = data.unstack().transpose().reset_index()
    data.columns = ['tranche_prime', 'tranche_salaire', 'effectif']
    data['cout'] = data.tranche_salaire * data.tranche_prime * data.effectif
    y = data.groupby('tranche_salaire')['cout'].sum()
    couts_cumul = y.cumsum()
    couts_cumul = couts_cumul / y.sum()
    effectifs_cumul= data.groupby('tranche_salaire')['effectif'].sum()
    effectifs_cumul = effectifs_cumul.cumsum() / effectifs_cumul.sum()
    x = data.tranche_salaire.unique() / effectifs_cumul.sum()
    print simps(couts_cumul, effectifs_cumul)
    plt.plot(effectifs_cumul, couts_cumul, marker = 'o', label = '{}'.format(annee), color = 'r')
    plt.legend(loc = 2)

#plt.plot([0, 0.5, 1], [0, 0.5, 1])






def plot_tranche_prime_moyenne_par_sn(data, annee):

    data = data.unstack().transpose().reset_index()

    data.columns = ['tranche_prime', 'tranche_salaire', 'compte']

    data['tranch_prim_times_effectifs'] = data.tranche_prime * data.compte
    x = data.groupby('tranche_salaire')['compte'].sum().reset_index()
#    z = data.merge(x, on = "tranche_salaire", how ='outer')

    somme_tranche_prime_times_effectifs = data.groupby('tranche_salaire')['tranch_prim_times_effectifs'].sum().reset_index()
    result = somme_tranche_prime_times_effectifs.merge(x)
    result['mean_prime'] = result['tranch_prim_times_effectifs'] / result.compte
    fusion = data.merge(result, on = 'tranche_salaire', how = 'outer')
    fusion.columns = [
        'tranche_prime',
        'tranche_salaire',
        'effectif',
        'tranche_prime_times_effectif',
        'tranche_prime_times_effectifs_dans_tranche_snm',
        'effectif_dans_tranche_snm',
        'mean_prime'
        ]
    fusion['diff_mean_squared'] = (fusion.tranche_prime - fusion.mean_prime) ** 2
    fusion['effectifs_times_diff_mean_squared'] = fusion.diff_mean_squared * fusion.effectif

    print fusion.head()
    var_num = fusion.groupby('tranche_salaire')['effectifs_times_diff_mean_squared'].sum()
    var_denum = fusion.groupby('tranche_salaire')['effectif_dans_tranche_snm'].unique()
    variance = var_num / var_denum
    ecart_type = variance ** 0.5

    mean_minus_half_std = fusion.mean_prime.unique() - 0.5 * ecart_type
    mean_plus_half_std = fusion.mean_prime.unique() + 0.5 * ecart_type
    plt.plot(result.tranche_salaire, result.mean_prime, color = 'r', marker = 'o', label = 'taux de prime moyen par SNM en {}'.format(annee))
    plt.legend()
    plt.plot(result.tranche_salaire, mean_minus_half_std, color = 'r', linestyle = '--', )
    plt.plot(result.tranche_salaire, mean_plus_half_std, color = 'r', linestyle = '--')

    return ecart_type

def plot_tranche_prime_mediane_par_sn(data, annee, decile):
    data = data.unstack().transpose().reset_index()

    data.columns = ['tranche_prime', 'tranche_salaire', 'compte']

    data['tranch_prim_times_effectifs'] = data.tranche_prime * data.compte
    x = data.groupby('tranche_salaire')['compte'].sum().reset_index()
#    z = data.merge(x, on = "tranche_salaire", how ='outer')

    somme_tranche_prime_times_effectifs = data.groupby('tranche_salaire')['tranch_prim_times_effectifs'].sum().reset_index()
    result = somme_tranche_prime_times_effectifs.merge(x)
    x = data.groupby('tranche_salaire')['compte'].sum().reset_index()
    x['compte_premier_decile'] = x['compte'] / 10
    x['compte_dernier_decile'] = x['compte'] / 10 * 9
    x['compte_median'] = x['compte'] / 2
    z = data.merge(x, on = "tranche_salaire", how ='outer')
    tranche_pr_med = list()
    for tranche_salaire, id_median in zip(z.tranche_salaire.unique(), z.compte_median.unique()):
        data_salaire = data[data['tranche_salaire'] == tranche_salaire]
        data_salaire['cumsum_compte'] = data_salaire['compte'].cumsum()
        data_salaire_med = data_salaire[data_salaire['cumsum_compte'] >= id_median]
        data_salaire_med = data_salaire_med[data_salaire_med['cumsum_compte'] == data_salaire_med.cumsum_compte.min()]
        medianes = data_salaire_med['tranche_prime']
        if len(medianes) != 1:
            medianes = 0
        tranche_pr_med.append(medianes)
    result['tranche_pr_med'] = tranche_pr_med
    plt.plot(
        result.tranche_salaire,
        result['tranche_pr_med'],
        marker = 'o',
        color = 'b',
        label = "tx de prime, mediane par tranche de salaire net en {}".format(annee)
        )
    plt.legend(loc = 2, fontsize = 10)

    if decile:

        dernier_decile = list()
        for tranche_salaire, id_dernier_decile in zip(z.tranche_salaire.unique(), z.compte_dernier_decile.unique()):
            data_salaire = data[data['tranche_salaire'] == tranche_salaire]
            data_salaire['cumsum_compte'] = data_salaire['compte'].cumsum()
            data_salaire_premier_dec = data_salaire[data_salaire['cumsum_compte'] >= id_dernier_decile]
            data_salaire_premier_dec = data_salaire_premier_dec[data_salaire_premier_dec['cumsum_compte'] == data_salaire_premier_dec.cumsum_compte.min()]
            premiers_deciles = data_salaire_premier_dec['tranche_prime']

            dernier_decile.append(premiers_deciles)
        result['tranche_pr_dernier_dec'] = dernier_decile
        plt.plot(result.tranche_salaire, result['tranche_pr_dernier_dec'],
                 linestyle = '--',
                 label = "tx de prime, dernier decile par tranche de salaire net en {}".format(annee),
                 color = 'b')
        plt.legend(loc = 2, fontsize = 10)

        premier_decile = list()
        for tranche_salaire, id_premier_decile in zip(z.tranche_salaire.unique(), z.compte_premier_decile.unique()):
            data_salaire = data[data['tranche_salaire'] == tranche_salaire]
            data_salaire['cumsum_compte'] = data_salaire['compte'].cumsum()
            data_salaire_premier_dec = data_salaire[data_salaire['cumsum_compte'] >= id_premier_decile]
            data_salaire_premier_dec = data_salaire_premier_dec[data_salaire_premier_dec['cumsum_compte'] == data_salaire_premier_dec.cumsum_compte.min()]
            premiers_deciles = data_salaire_premier_dec['tranche_prime']

            premier_decile.append(premiers_deciles)
        result['tranche_pr_premier_dec'] = premier_decile
        plt.plot(result.tranche_salaire, result['tranche_pr_premier_dec'],
                 linestyle = '--',
                 color = 'b',
                 label = "tx de prime, 1er decile par tranche de salaire net en {}".format(annee))
        plt.legend(loc = 2, fontsize = 10)
