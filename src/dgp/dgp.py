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


def generate_factor_panel(
        num_units=30,
        num_periods=60,
        treatment_start_period=40,
        treatment_effect=-0.05,
        num_treated_units=10,
        base_time_trend=0.02,
        seed=42,
        hetero_baseline=False,
        hetero_treatment_effect=False,
        non_stationary_errors=False,
        structural_break=False):
    """
    Interacted fixed-effects factor model panel generator with treatment starting at a chosen period.

    Parameters
    ----------
    num_units : int
        Number of units/geos.
    num_periods : int
        Number of time periods.
    treatment_start_period : int
        First period where treated units switch on treatment.
    treatment_effect : float
        Baseline treatment effect (ATE/MDE) applied to treated units after start.
    num_treated_units : int
        Number of units assigned to treatment.
    base_time_trend : float
        Slope of deterministic time trend shared by all units.
    seed : int
        Random seed for reproducibility.
    hetero_baseline : bool
        If True, inflate variance of unit fixed effects to create large baseline gaps.
    hetero_treatment_effect : bool
        If True, draw unit-level treatment effects around the baseline effect.
    non_stationary_errors : bool
        If True, add a random-walk error component.
    structural_break : bool
        If True, add a global shock beginning at the treatment start (affects all units).

    Returns
    -------
    pd.DataFrame
        Panel data with columns: unit, time, treated_unit, treatment, Y_it, and latent drivers.
    """
    if num_treated_units > num_units:
        raise ValueError("The number of treated units cannot exceed the total number of units.")

    rng = np.random.default_rng(seed)

    units = [f'{chr(65+i//26)}{chr(65+i%26)}' for i in range(num_units)]
    periods = np.arange(num_periods)

    data = pd.DataFrame({
        'unit': np.repeat(units, num_periods),
        'time': np.tile(periods, num_units),
    })

    treated_units = rng.choice(units, num_treated_units, replace=False)
    data['treated_unit'] = data['unit'].isin(treated_units)
    data['treatment'] = data['treated_unit'] & (data['time'] >= treatment_start_period)

    # Unit fixed effects with optional large heterogeneity
    unit_sd = 0.15 if hetero_baseline else 0.05
    unit_effects = rng.normal(0, unit_sd, size=num_units)
    data['unit_effect'] = data['unit'].map(dict(zip(units, unit_effects)))

    # Deterministic time trend
    time_trend = periods * base_time_trend
    data['time_trend'] = data['time'].map(dict(zip(periods, time_trend)))

    # Latent factors (interacted fixed effects)
    num_factors = 2
    loadings = rng.normal(0, 0.5, size=(num_units, num_factors))
    factors = rng.normal(0, 1.0, size=(num_periods, num_factors))
    for k in range(num_factors):
        data[f'factor_loading_{k+1}'] = data['unit'].map(dict(zip(units, loadings[:, k])))
        data[f'time_factor_{k+1}'] = data['time'].map(dict(zip(periods, factors[:, k])))

    interacted_effect = sum(data[f'factor_loading_{k+1}'] * data[f'time_factor_{k+1}'] for k in range(num_factors))

    # Treatment effects (heterogeneous if requested)
    unit_te = np.full(num_units, treatment_effect)
    if hetero_treatment_effect:
        unit_te = rng.normal(loc=treatment_effect, scale=abs(treatment_effect) * 0.5 + 0.02, size=num_units)
    data['unit_treatment_effect'] = data['unit'].map(dict(zip(units, unit_te)))

    # Structural break affecting everyone from treatment start onward
    global_shock = np.zeros(num_periods)
    if structural_break:
        post_horizon = num_periods - treatment_start_period
        shock_path = rng.normal(0.1, 0.05, size=post_horizon)
        global_shock[treatment_start_period:] = shock_path
    data['global_shock'] = data['time'].map(dict(zip(periods, global_shock)))

    # Error process: iid vs random walk
    if non_stationary_errors:
        innovations = rng.normal(0, 0.05, size=(num_units, num_periods))
        errors = np.cumsum(innovations, axis=1)
    else:
        errors = rng.normal(0, 0.05, size=(num_units, num_periods))
    error_lookup = {
        unit: err_path
        for unit, err_path in zip(units, errors)
    }
    data['epsilon'] = data.apply(lambda row: error_lookup[row['unit']][row['time']], axis=1)

    outcome = (
        data['unit_effect'] +
        data['time_trend'] +
        interacted_effect +
        data['treatment'] * data['unit_treatment_effect'] +
        data['global_shock'] +
        data['epsilon']
    )

    data['Y_it'] = outcome

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
    
