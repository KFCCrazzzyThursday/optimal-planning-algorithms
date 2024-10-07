%reset -f
%run -i setup 5

def n_click_after_move(row):
    if any(t is None for t in row.click_times):
        print('Undefined click time. Excluding trial')  # only happens once
        return -1
    first_act = min(row.action_times)
    return sum(t > first_act for t in row.click_times)

tdf['n_click_after_move'] = tdf.apply(n_click_after_move, axis=1)
tdf = tdf.query('n_click_after_move != -1')
tdf['clicked_after_move'] = tdf.n_click_after_move > 0

write_tex('interleave_percent_trials', f'{tdf.clicked_after_move.mean()*100:.1f}')

sum(tdf.groupby('wid').clicked_after_move.sum() > 2)

# %% --------
all_trials = pd.read_pickle(f'../data/exp{EXPERIMENT}/trials.pkl')
all_trials['n_click_after_move'] = all_trials.apply(n_click_after_move, axis=1)
all_trials['clicked_after_move'] = all_trials.n_click_after_move > 0
sum(all_trials.query('block != "test"').groupby('wid').clicked_after_move.sum() > 0)


# %% --------

@figure()
def interleaved():
    # all_trials.clicked_after_move.groupby('wid').mean().sort_values(ascending=False).plot\
    #     .bar(width=.9, color="gray", label="Practice", alpha=0.5)
    tdf.clicked_after_move.groupby('wid').mean().sort_values(ascending=False).plot\
        .bar(width=.9, color="black", label="Test", alpha=1)
    plt.xticks(range(9, 50, 10), map(str, range(10, 51, 10)), rotation=0)
    plt.ylim(0, 1)
    plt.xlabel('Participant')
    plt.ylabel('Proportion of test trials\nwith clicks after first move')

