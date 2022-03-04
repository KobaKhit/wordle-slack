import streamlit as st
import pandas as pd
import re
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('dark_background') 

from torch import mean
st.set_page_config(layout="wide")



white_square = '⬜'
yellow_square = '🟨'
green_square = '🟩'

st.title('Jornaya Wordle')

df = pd.read_json('wordles.json')

# update emojis
def board(x):
    return '<div style = "display:inline;width:300px;">{}</div>'.format(x)

def make_list(x):
    return '<ul style="list-style:none">{}</ul>'.format(
                ''.join(['<li>' + a + '</li>' for a in x.split('\n')]))

def display_day(header,game_list, n_games, avg_tries):
    st.header(header)
    st.markdown(f'##### {n_games} games played. Average number of guesses is {round(avg_tries,2)}'  )
    st.write(game_list,unsafe_allow_html = True)



df['board'] = df.board \
        .apply(lambda x: re.sub(':large_green_square:',green_square, x)) \
        .apply(lambda x: re.sub(':large_yellow_square:',yellow_square, x)) \
        .apply(lambda x: re.sub(':black_large_square:|:white_large_square:',white_square,x)) \
        .apply(make_list) \
        .apply(board)

# create list of wordle games dictionaries
wordles = []
for w in reversed(sorted(df.wordle.unique())):
    temp = df[df.wordle == w]
    header = 'Wordle {}'.format(w)

    listt = []
    for i,r in temp.iterrows():
        game = r['first_name'] + f" {r['tries']}/6" 
        if r['hardmode']:
            game = game + '*'
        # st.write(game,unsafe_allow_html = True)
        listt.append({'game': game,'board':r['board'],'tries': r['tries']})

    n_games = len(listt)
    avg_tries = sum(a['tries'] for a in listt)/n_games
    game_list = '<ul style="list-style: none;">' + ''.join(['<li style="float:left"><p>{}</p>{}</li>'.format(b['game'],b['board']) for b in listt]) + '<ul>'
    # st.write(game_list,unsafe_allow_html = True)
    wordles.append({'h':header,'game_list':game_list, 'n_games': n_games,'avg_tries':avg_tries})


# Display most recent wordle
col11, col12 = st.columns([1,3])
with col11:
    input_wordle = st.selectbox('', [w['h'] for w in wordles])

most_recent = next(w for w in wordles if w['h'] == input_wordle)
display_day(most_recent['h'], most_recent['game_list'],most_recent['n_games'], round(most_recent['avg_tries'],2))


#
col1, col2, col3 = st.columns([2, 2, 4])

# Totals Table
with col1:
     temp = df.groupby(['name','first_name']).agg({'tries':['mean','count']}).reset_index()[['first_name','tries']].rename(columns={'count':'games'})
     temp.columns = temp.columns.get_level_values(1)
     temp = temp.rename(columns={'mean': 'avg guesses','games': 'games played','':'first name'}).sort_values(by='first name', ascending = True)
     st.markdown('**Totals**')
     st.dataframe(temp)
     st.write(f'It takes {round(df.tries.mean(),4)} guesses on average overall across {str(df.shape[0])} games',)
    #  st.metric('Avg # of Guesses',round(df.tries.mean(),2))


# Guess Histogram
with col2:
    p = df.tries.hist(grid = False, figsize = (5,3.5), bins = range(1,8), align = 'left', ec='black')
    # plt.xticks(range(1,7))
    p.set_ylabel('Count')
    p.set_xlabel('Guesses')
    plt.suptitle('Histogram of Number of Guesses')
    
    st.pyplot(p.figure)

# Line graph
with col3:
    temp = df.groupby('wordle').agg({'tries':'mean'}).rename(columns = {'tries':'guesses'})
    p = temp.plot(ylim = [1,6], title = 'Average Number of Guesses', legend = False)
    p.set_ylabel("guesses")
    plt.rcParams["figure.figsize"] = (8,2.4)
    st.pyplot(p.figure)

# All games
st.header('Previous Games')
for w in wordles:
    display_day(w['h'],w['game_list'], w['n_games'],w['avg_tries'])

