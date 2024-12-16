import numpy as np
import pandas as pd

def generate_grouped_data(num_units=20, num_periods=50, treatment_start_period=40, treatment_effect=-0.05,
                          num_covariates=3, num_treated_units=5,base_time_trend=0.05, parallel_trends=True):
    
    if num_treated_units > num_units:
        raise ValueError("The number of treated units cannot exceed the total number of units.")
    
    np.random.seed(42)
    
    # Generate unit and time indices
    states = [f'{chr(65+i//26)}{chr(65+i%26)}' for i in range(num_units)]
    periods = np.arange(num_periods)
    
    # Init data
    data = pd.DataFrame({
        'unit': np.repeat(states, num_periods),
        'time': np.tile(periods, num_units),
    })
    
    # Create covariates
    for i in range(1, num_covariates + 1):
        data[f'X{i}'] = np.random.normal(loc=0, scale=1, size=num_periods * num_units)

    # Assign treatment
    treated_states = np.random.choice(states, num_treated_units, replace=False)
    data['treated_unit'] = data['unit'].isin(treated_states)
    data['treatment'] = data['unit'].isin(treated_states) & (data['time'] >= treatment_start_period)
    
    # Fixed effects for units and time
    unit_effects = np.random.normal(loc=0, scale=0.1, size=num_units)
    time_effects = np.random.normal(loc=0, scale=0.02, size=num_periods)
    
    # Adding fixed effects
    data['unit_effect'] = data['unit'].map(dict(zip(states, unit_effects)))
    data['time_effect'] = data['time'].map(dict(zip(periods, time_effects)))

    # Time trend
    if parallel_trends:
        time_trend = np.arange(num_periods) * base_time_trend
        data['time_trend'] = data['time'].map(dict(zip(periods, time_trend)))
    else:
        treated_trend = np.arange(num_periods) * base_time_trend
        control_trend = np.arange(num_periods) * base_time_trend / 2
        data['time_trend'] = np.where(data['treated_unit'], 
                                      data['time'].map(dict(zip(periods, treated_trend))),
                                      data['time'].map(dict(zip(periods, control_trend))))
        
    # Simulate outcome variable Y_it with unit-specific linear trends
    outcome_model = (data['unit_effect'] +
                     data['time_effect'] +
                     data['time_trend'] +
                     data['treatment'] * treatment_effect)
    
    for i in range(1, num_covariates + 1):
        outcome_model += data[f'X{i}'] * np.random.uniform(-0.1, 0.1)
    
    data['Y_it'] = outcome_model + np.random.normal(loc=0, scale=0.1, size=num_periods * num_units)
    
    return data


def ab_test_dgp(
        n_users, 
        n_confounders, 
        n_features,
        homogeneous=False, 
        endogenous=False, 
        treatment_effect_func=lambda x: np.exp(2 * x[0]), 
        seed=123):
    
    # Seed
    np.random.seed(seed)

    # Variables/Confounders
    W = np.random.normal(0, 1, size=(n_users, n_confounders))

    # Treatment Effect
    X = W[:, np.random.choice(n_confounders, n_features, replace=False)]
    TE = np.array([treatment_effect_func(x_i) for x_i in X])

    if homogeneous:
        TE = np.full_like(TE, TE.mean())

    # Treatment Assignment
    if endogenous:
        beta = np.random.uniform(-1, 1, size=n_confounders)
        eta = np.random.uniform(-1, 1, size=n_users)
        treatment_prob = expit(np.dot(W, beta) + eta)
        T = np.random.binomial(1, treatment_prob)
    else:
        T = np.random.binomial(1, 0.5, n_users)

    # Outcome
    coefs_y = np.random.uniform(0, 1, size=n_confounders)
    epsilon_y = np.random.uniform(0, 1, size=n_users)
    Y = TE * T + np.dot(W, coefs_y) + epsilon_y

    # Dataframe
    df = pd.DataFrame(W, columns=[f"W{i}" for i in range(1, n_confounders + 1)])
    df['T'] = T
    df['TE'] = TE 
    df['Y'] = Y

    return df
    
