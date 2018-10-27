import numpy as np

def _check_names(expected_columns, df):
    in_both = expected_columns.intersection(set(df.columns))
    if in_both != expected_columns:
        raise RuntimeError('Columns ' + ', '.join(expected_columns - in_both) + ' missing!')


def _expected_score(rating1, rating2):
    return 1.0 / (1 + 10 ** ((rating2 - rating1)/400.0))


def _update_rating(rating, expected, result, k):
    return rating + k * (result - expected)

def _update(rating, team, opponent_rating, result, k):
    if result == 'draw':
        result = 0.5
    elif result == team:
        result = 1
    else:
        result = 0
    expected = _expected_score(rating, opponent_rating)
    return _update_rating(rating, expected, result, k)


def _check_result_column(df):
    result_values = df['result'].values 
    expected = list(np.unique(df[['home_team', 'away_team']].values)) + ['draw']
    unique_values = np.unique(result_values)
    if not all([x in expected for x in list(unique_values)]):
        raise RuntimeError('Values in result column should be team name or draw ' +
                           'found ' + ', '.join(list(unique_values)[0:10]))


def compute(df, k = 22, start = 1500):
    expected_columns = ['home_team', 'away_team', 'result']
    _check_names(set(expected_columns), df)
    _check_result_column(df)
    elo_ranks = {}
    datamatrix = df[expected_columns].values
    n_rows, _ = datamatrix.shape
    result_mat = np.zeros((n_rows, 2))
    for i in range(0, n_rows):
        home_team = datamatrix[i, 0]
        away_team = datamatrix[i, 1]
        home_elo = elo_ranks.get(home_team, start)
        away_elo = elo_ranks.get(away_team, start)
        new_home_elo = _update(home_elo, home_team, away_elo, datamatrix[i,2], k)
        new_away_elo = _update(away_elo, away_team, home_elo, datamatrix[i,2], k)
        elo_ranks[home_team] = new_home_elo
        elo_ranks[away_team] = new_away_elo
        result_mat[i, 0] = new_home_elo
        result_mat[i, 1] =    new_away_elo
    return result_mat, elo_ranks
        
if __name__ == "__main__":
    import pandas as pd
    df = pd.DataFrame([
        {
            'home_team': 'b',
            'away_team': 'a',
            'result': 'draw'
        },
        {
            'home_team': 'a',
            'away_team': 'c',
            'result': 'a'
        },
        {
            'home_team': 'a',
            'away_team': 'c',
            'result': 'a'
        },
        {
            'home_team': 'a',
            'away_team': 'c',
            'result': 'c'
        }
    ])    
    print(df)
    mat, ranks = compute(df)
    print(mat)
    print(ranks)
