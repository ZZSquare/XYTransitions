import plotly.graph_objects as go
import pandas as pd
from ExactSolution import Hamiltonianm, negHamiltonianm
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

def lrtranslated(fig, df, i, points, error):
    lr = LinearRegression().fit(np.array(df['Translated'][i - points:i + points]+error).reshape(-1, 1),
                                df['Bz'][i - points:i + points])
    #print(df['Scaled'][i - points:i + points])
    #nparr = np.arange(0.0, -1.0, -0.01)
    nparr = np.arange(1.0, 0.0, -0.01)
    fig.add_trace(go.Scatter(x=nparr * lr.coef_ + lr.intercept_, y=nparr, name='Regression'+str(points)+str(error)+'tr',
                             mode='lines', visible="legendonly"))
    return lr.predict([[0.5]])

def calculateregressiontranslated(fig, df, points, error, folder):
    i = 0
    while True:
        #if df['Translated'][i] > -0.50:
        if df['Translated'][i] < 0.50:
            break
        i += 1

    with open(folder+"regression translated.txt", "a") as f:
        total = 0
        for n in range(1, points+1):
            result = lrtranslated(fig, df, i, n, error)
            total += result[0]
            f.write(str(result[0])+ ' ')
        f.write(str(total/points))
        f.write('\n')

def lrscaled(fig, df, i, points, error):
    lr = LinearRegression().fit(np.array(df['Scaled'][i - points:i + points]+error).reshape(-1, 1),
                                df['Bz'][i - points:i + points])
    #print(df['Scaled'][i - points:i + points])
    nparr = np.arange(1.0, 0.0, -0.01)
    #nparr = np.arange(0.0, -1.0, -0.01)
    fig.add_trace(go.Scatter(x=nparr * lr.coef_ + lr.intercept_, y=nparr, name='Regression'+str(points)+str(error)+'sc',
                             mode='lines', visible="legendonly"))
    #plt.plot(nparr * lr.coef_ + lr.intercept_, nparr, color=color, linestyle='-', label=label)
    return lr.predict([[0.5]])

def calculateregressionscaled(fig, df, points, error, folder):
    i = 0
    while True:
        #if df['Scaled'][i] > -0.50:
        if df['Scaled'][i] < 0.50:
            print(i)
            break
        i += 1

    with open(folder+"regression scaled.txt", "a") as f:
        total = 0
        colors = ['orange', 'green', 'aqua']
        for n in range(1, points+1):
            #result = lrscaled(fig, df, i, 4, error, color, label)\
            result = lrscaled(fig, df, i, n, error)
            total += result[0]
            f.write(str(result[0])+ ' ')
        f.write(str(total/points))
        f.write('\n')


folder = '413\\'
f1 = 'J=1.000 Bx=0.030 dB=0.010 BzMax=2.000 dt=2.000 gamma=3.000' + '.csv'
f2 = 'J=1.000 Bx=0.050 dB=0.010 BzMax=2.000 dt=1.600 gamma=4.000' + '.csv'
f3 = 'J=1.000 Bx=0.100 dB=0.010 BzMax=2.000 dt=0.900 gamma=5.000' + '.csv'
files = [folder+f1, folder+f2, folder+f3]
calibratedfiles = [folder+'Calibrated '+f1, folder+'Calibrated '+f2, folder+'Calibrated '+f3]
simulatedfiles = [folder+'FakeSantiago\\'+f1, folder+'FakeSantiago\\'+f2, folder+'FakeSantiago\\'+f3]
#file1 = folder + 'J=1.000 Bx=0.030 dB=0.010 BzMax=2.000 dt=2.000 gamma=3.000.csv'
#file2 = folder + 'Calibrated J=1.000 Bx=0.100 dB=0.010 BzMax=2.000 dt=0.900 gamma=5.000.csv'
#file3 = folder + 'FakeSantiago\J=1.000 Bx=0.100 dB=0.010 BzMax=2.000 dt=0.900 gamma=5.000.csv'
plottitle = folder + 'Bx=0.1t.html'
Bx = [0.03, 0.05, 0.1]


fig = go.Figure()

n = 0
while n < len(files):
#while n < 1:
    #hm, x = negHamiltonianm(1, Bx[n])
    hm, x = Hamiltonianm(1, Bx[n])

    df = pd.read_csv(files[n])
    calibrated_df = pd.read_csv(calibratedfiles[n])
    simulated_df = pd.read_csv(simulatedfiles[n])

    #diff = 1 + df['mz'][0] \
    diff = 1 - df['mz'][0]
    #print(diff)
    mult = 1/df['mz'][0]

    df['Translated'] = df['mz']+diff
    #df['Translated'] = df['mz']-diff
    #df['Scaled'] = -df['mz']*mult
    df['Scaled'] = df['mz'] * mult


    fig.add_trace(go.Scatter(x=df['Bz'], y=df['mz'], name=str(Bx[n])+'Circuit', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Translated'], name=str(Bx[n])+'Translated', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Scaled'], name=str(Bx[n])+'Scaled', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=calibrated_df['Bz'], y=calibrated_df['mz'], name=str(Bx[n])+'Calibrated', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=simulated_df['Bz'], y=simulated_df['mz'], name=str(Bx[n])+'Simulator', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=x, y=hm, name=str(Bx[n])+'Exact', mode='lines'))
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Exact'], name=str(Bx[n])+'Trotter', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Interaction'], name=str(Bx[n])+'Interaction', mode='lines+markers'))
    #plt.plot(df['Bz'][5:-5], df['Scaled'][5:-5], 'blue')
    #plt.plot(df['Bz'], df['Scaled'], 'blue')

    calculateregressiontranslated(fig, df, 4, 0, folder)
    calculateregressiontranslated(fig, df, 4, 0.02, folder)
    calculateregressiontranslated(fig, df, 4, -0.02, folder)
    calculateregressionscaled(fig, df, 4, 0, folder)
    calculateregressionscaled(fig, df, 4, 0.02, folder)
    calculateregressionscaled(fig, df, 4, -0.02, folder)
    #calculateregressionscaled(fig, df, 1, 0, folder, 'orange', 'original')
    #calculateregressionscaled(fig, df, 1, 0.02, folder, 'orchid', '+ 0.02')
    #calculateregressionscaled(fig, df, 1, -0.02, folder, 'teal', '- 0.02')

    n+=1

# fig.add_trace(go.Scatter(x=df['Bz'], y=thetaarray, name='Theta', mode='markers'), secondary_y=True)
fig.update_xaxes(title_text="Bz")
fig.update_yaxes(title_text="mz")
# fig.update_yaxes(title_text="theta", secondary_y=True)
#fig.show()
#fig.write_html(folder+'plotall.html')

'''
plt.xlabel('$B_z$ Field Magnitude', fontsize=22)
plt.ylabel('$m_z$', fontsize=22)
plt.title('Bx = 0.03 Scaled 8 Points', fontsize=24)
plt.legend()
plt.axhline(y=0.5, color='brown', linestyle='-.')
plt.show()
'''
