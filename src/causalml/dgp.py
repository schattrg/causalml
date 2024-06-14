import numpy as np
import pandas as pd

def generate_grouped_data(num_units=20, num_periods=50, treatment_start_period=40, treatment_effect=-0.05,
                          num_covariates=3, num_treated_units=5, base_trend_slope=0.0, parallel_trends=True):
    
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
    
    # Optional unit-specific trends
    if parallel_trends:
        # Apply a small random variation to the base trend slope for each unit
        unit_trend_variations = np.random.normal(loc=base_trend_slope, scale=0.00, size=num_units)
    else:
        # Apply larger variations to create noticeable divergences in trends
        unit_trend_variations = np.random.normal(loc=base_trend_slope, scale=base_trend_slope*2, size=num_units)
    
    data['unit_trend'] = data['unit'].map(dict(zip(states, unit_trend_variations)))

    # Simulate outcome variable Y_it with unit-specific linear trends
    outcome_model = (data['unit_effect'] +
                     data['time_effect'] +
                     data['treatment'] * treatment_effect +
                     data['unit_trend'] * data['time'])
    
    for i in range(1, num_covariates + 1):
        outcome_model += data[f'X{i}'] * np.random.uniform(-0.1, 0.1)
    
    data['Y_it'] = outcome_model + np.random.normal(loc=0, scale=0.1, size=num_periods * num_units)
    
    return data
