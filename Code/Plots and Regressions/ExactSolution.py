import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy.linalg as LA


X = np.matrix([[0, 1.0], [1.0, 0]], dtype='complex128')
Y = np.matrix([[0, -1.0j], [1.0j, 0]], dtype='complex128')
Z = np.matrix([[1.0, 0], [0, -1.0]], dtype='complex128')
I = np.matrix([[1.0, 0], [0, 1.0]], dtype='complex128')
XY_MATRIX = np.kron(X, X) + np.kron(Y, Y)
BX_MATRIX = np.kron(I, X) + np.kron(X, I)
BY_MATRIX = np.kron(I, Y) + np.kron(Y, I)
BZ_MATRIX = np.kron(I, Z) + np.kron(Z, I)

def XYMatrix(J):
    return J * (-0.25) * XY_MATRIX

def BxMatrix(Bx):
    return Bx * BX_MATRIX

def ByMatrix(By):
    return By * BY_MATRIX

def BzMatrix(Bz):
    return Bz * BZ_MATRIX

def XYHamiltonian(XY, B_x, Bz):
    return XY + B_x + BzMatrix(Bz)

def Hamiltonianm(J, Bx):
    XY = XYMatrix(J)
    B_x = BxMatrix(Bx)
    mzarray = []
    Bzarray = np.arange(1.25, 0, -0.01)
    transition = False

    for bz in Bzarray:
        eigenvalue, eigenvector = LA.eigh(XYHamiltonian(XY, B_x, bz))
        #print(eigenvalue)
        psi = np.matrix(eigenvector[0])
        m = np.matmul(psi, np.matmul(BzMatrix(1), psi.getH()))
        mzarray.append(-np.real(m.item(0)) / 2)
        if transition==False and (-np.real(m.item(0)) / 2) < 0.5:
            #print(bz)
            transition=True
    return mzarray, Bzarray

def negHamiltonianm(J, Bx):
    XY = XYMatrix(J)
    B_x = BxMatrix(Bx)
    mzarray = []
    Bzarray = np.arange(-2, 0, 0.0001)
    transition = False

    for bz in Bzarray:
        eigenvalue, eigenvector = LA.eigh(XYHamiltonian(XY, B_x, bz))
        #print(eigenvalue)
        psi = np.matrix(eigenvector[3])
        m = np.matmul(psi, np.matmul(BzMatrix(1), psi.getH()))
        mzarray.append(np.real(m.item(0)) / 2)
        if transition==False and (-np.real(m.item(0)) / 2) > 0.5:
            print(bz)
            transition=True
    return mzarray, Bzarray

def showfig(df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    hm, x = Hamiltonianm(1, 0.05)

    fig.add_trace(go.Scatter(x=df['Bz'], y=df['mz'], name='Circuit', mode='lines'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Exact'], name='Exact', mode='lines'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Interaction'], name='Interaction', mode='lines'), secondary_y=False)
    fig.add_trace(go.Scatter(x=x, y=hm, name='Hamiltonian', mode='lines'), secondary_y=False)

    #title = "J=" + str(J) + " Bx=" + str(Bx) + " gamma=" + str(gamma) + " dt_steps=" + str(dt_steps)
    #fig.update_layout(title_text=title)
    fig.update_xaxes(title_text="Bz")
    fig.update_yaxes(title_text="mz", secondary_y=False)
    fig.show()


Hamiltonianm(1, 0)