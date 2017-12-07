#!/usr/bin/env python
# encoding: utf-8

# INPUT:    'data.csv'
# OUTPUT:   'Regressor.pkl'

import os
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
import pickle
# os.chdir('D:\workspace\TwCrawler')

def makeRegressor(dataFile, nFeatures, nIteration):
    # input data containing matched X and Y
    data = pd.read_csv(dataFile, sep='w')
    data = data.drop(['Unnamed: 0', '_'], axis=1)
    data = data.dropna(subset=['Y30'])
    # subsetting X and Y from dataset
    _ = nFeatures
    X = data.drop(['date', 'x9', 'x10', 'Y30'], axis=1)         # <- select diff. numbers of features
    X = X[X.columns[0:59]]
    y = data['Y30']                             # <- select diff. prediction day intervals

    score = 0.0
    # multiple tests
    for i in range(nIteration):
        # split train data and test data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

        # instantiate Regressor
        rgs = MLPRegressor(alpha=0.003, max_iter=1000, hidden_layer_sizes=50)

        # train model
        rgs.fit(X_train, y_train)

        # test model with R^2
        Rsquared = rgs.score(X_test, y_test)
        print('Trial:', i, 'R^2:', Rsquared)


    return(rgs, Rsquared)


if __name__ == '__main__':
    rg, score = makeRegressor('data.csv', 5)

    with open('Regressor.pkl', 'wb') as f:
        pickle.dump(rg, f)

'''
with open('filename.pkl', 'rb') as f:
    clf = pickle.load(f)
MLPRegressor(activation='relu', alpha=0.0001, batch_size='auto', beta_1=0.9,
       beta_2=0.999, early_stopping=False, epsilon=1e-08,
       hidden_layer_sizes=(100,), learning_rate='constant',
       learning_rate_init=0.001, max_iter=200, momentum=0.9,
       nesterovs_momentum=True, power_t=0.5, random_state=None,
       shuffle=True, solver='adam', tol=0.0001, validation_fraction=0.1,
       verbose=False, warm_start=False)
'''
