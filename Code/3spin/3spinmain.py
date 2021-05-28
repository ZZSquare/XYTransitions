import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from qiskit.ignis.mitigation.measurement import complete_meas_cal, CompleteMeasFitter
from qiskit import Aer, QuantumRegister, QuantumCircuit, execute, IBMQ, ClassicalRegister, transpile
from qfunctions3spin import adiabaticramp, theta, threespin_instruction, exactm, interactionm


def threespin_df(J, Bx, dB, Bz_max, dt_steps, dt_steps_bool, gamma, skip, provider, backend, pq0, pq1, pq2):
    count_list = []
    calibrated_count_list = []
    tarray, Bzarray, dt_or_steps, _ = adiabaticramp(J, Bx, dB, Bz_max, dt_steps, dt_steps_bool, gamma)

    if dt_steps_bool == 'dt':
        dt = dt_steps
    else:
        dt = dt_or_steps

    thetaarray, _ = theta(Bzarray, dt)

    # Calibration Matrix
    calqr = QuantumRegister(3)
    meas_calibs, state_labels = complete_meas_cal(qubit_list=[0, 1, 2], qr=calqr, circlabel='3spin')
    t_cal = transpile(meas_calibs, provider.get_backend(backend), initial_layout={calqr[0]:pq0, calqr[1]:pq1, calqr[2]:pq2})
    cal_results = execute(t_cal, backend=provider.get_backend(backend), shots=5000).result()
    meas_fitter = CompleteMeasFitter(cal_results, state_labels, circlabel='3spin')
    #meas_fitter.plot_calibration()

    i = 0
    while (i < 21):
    #while (i < 5):
        print('Bz = %f' % (Bzarray[i]))
        qr = QuantumRegister(3, 'qr')
        cr = ClassicalRegister(3, 'cr')
        circ = QuantumCircuit(qr, cr)
        #circ.initialize([0, 0, 0, 0, 0, 0, 0, 1], [0, 1, 2])
        circ.x(0)
        circ.x(1)
        circ.x(2)

        threespin_instruction(circ, J, Bx, thetaarray[:i], dt)
        circ.measure([0, 1, 2], [0, 1 ,2])

        t_qc = transpile(circ, provider.get_backend(backend), initial_layout={qr[0]:pq0, qr[1]:pq1, qr[2]:pq2})
        #t_qc.draw()

        result = execute(t_qc, provider.get_backend(backend), shots=5000).result()
        counts = result.get_counts()
        counts['Time'] = tarray[i]
        counts['Bz'] = Bzarray[i]
        count_list.append(counts)
        with open("count_list.txt", "w") as output:
            output.write(str(count_list))

        mitigated_counts = meas_fitter.filter.apply(result).get_counts()
        mitigated_counts['Time'] = tarray[i]
        mitigated_counts['Bz'] = Bzarray[i]
        calibrated_count_list.append(mitigated_counts)
        with open("calibrated_count_list.txt", "w") as output:
            output.write(str(calibrated_count_list))

        i = i + 1 + skip

    # Creating dataframe
    df = pd.DataFrame(count_list)
    time_col = df.pop('Time')
    df.insert(0, 'Time', time_col)
    #df['Exact'] = exactm(J, Bx, Bzarray, dt)
    #df['Interaction'] = interactionm(J, Bx, thetaarray, dt)

    calibrated_df = pd.DataFrame(calibrated_count_list)
    time_col = df.pop('Time')
    df.insert(0, 'Time', time_col)

    if '000' not in df:
        df['000'] = 0
    if '001' not in df:
        df['001'] = 0
    if '010' not in df:
        df['010'] = 0
    if '011' not in df:
        df['011'] = 0
    if '100' not in df:
        df['100'] = 0
    if '101' not in df:
        df['101'] = 0
    if '110' not in df:
        df['110'] = 0
    if '111' not in df:
        df['111'] = 0
    df = df.fillna(0)

    if '000' not in calibrated_df:
        calibrated_df['000'] = 0
    if '001' not in calibrated_df:
        calibrated_df['001'] = 0
    if '010' not in calibrated_df:
        calibrated_df['010'] = 0
    if '011' not in calibrated_df:
        calibrated_df['011'] = 0
    if '100' not in calibrated_df:
        calibrated_df['100'] = 0
    if '101' not in calibrated_df:
        calibrated_df['101'] = 0
    if '110' not in calibrated_df:
        calibrated_df['110'] = 0
    if '111' not in calibrated_df:
        calibrated_df['111'] = 0
    calibrated_df = calibrated_df.fillna(0)

    # Calculating mz
    total = df['000'] + df['001']+ df['010'] + df['011'] + df['100'] + df['101'] + df['110'] + df['111']
    df['mz'] = -(1.5*df['000'] + 0.5*(df['001'] + df['010'] + df['100'] - df['011'] - df['101'] - df['110']) - 1.5*df['111']) / total
    calibrated_df['mz'] = -(1.5*df['000'] + 0.5*(df['001'] + df['010'] + df['100'] - df['011'] - df['101'] - df['110']) - 1.5*df['111']) / total

    # Creating Files
    if dt_steps_bool == 'dt':
        df.to_csv('5172\\3spin J={:.3f} Bx={:.3f} dB={:.3f} BzMax={:.3f} dt={:.3f} gamma={:.3f}.csv'.format(J, Bx, dB, Bz_max,
                                                                                                      dt_steps, gamma))
        calibrated_df.to_csv(
            '5172\\3spin Calibrated J={:.3f} Bx={:.3f} dB={:.3f} BzMax={:.3f} dt={:.3f} gamma={:.3f}.csv'.format(J, Bx, dB,
                                                                                                           Bz_max,
                                                                                                           dt_steps,
                                                                                                           gamma))
    else:
        df.to_csv(
            '3spin J={:.3f} Bx={:.3f} dB={:.3f} BzMax={:.3f} BzSteps={:.3f} gamma={:.3f}.csv'.format(J, Bx, dB, Bz_max,
                                                                                                     dt_steps, gamma))
        calibrated_df.to_csv(
            '3spin Calibrated J={:.3f} Bx={:.3f} dB={:.3f} BzMax={:.3f} BzSteps={:.3f} gamma={:.3f}.csv'.format(J, Bx,
                                                                                                                dB,
                                                                                                                Bz_max,
                                                                                                                dt_steps,
                                                                                                                gamma))

    return df, calibrated_df, dt_or_steps, thetaarray


def showfig(J, Bx, dB, Bz_max, dt_steps, dt, gamma, skip, provider, backend, pq0, pq1, pq2):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df, calibrated_df, _, thetaarray = threespin_df(J, Bx, dB, Bz_max, dt_steps, dt, gamma, skip, provider, backend, pq0, pq1, pq2)

    fig.add_trace(go.Scatter(x=calibrated_df['Bz'], y=calibrated_df['mz'], name='Calibrated', mode='lines'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['mz'], name='Circuit', mode='lines'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Exact'], name='Exact', mode='lines'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Interaction'], name='Interaction', mode='lines'), secondary_y=False)

    fig.add_trace(go.Scatter(x=df['Time'], y=thetaarray, name='Theta', mode='markers'), secondary_y=True)
    title = "J=" + str(J) + " Bx=" + str(Bx) + " gamma=" + str(gamma) + " dt_steps=" + str(dt_steps)
    fig.update_layout(title_text=title)
    fig.update_xaxes(title_text="Bz")
    fig.update_yaxes(title_text="mz")
    fig.update_yaxes(title_text="theta", secondary_y=True)
    fig.show()
    fig.write_html(title+'.html')



def main():

    # Set account credentials here
    #IBMQ_KEY =
    #IBMQ.save_account(IBMQ_KEY)
    #provider = Aer
    provider = IBMQ.load_account()

    # Set name of backend
    # eg. 'ibmq_santiago'
    backend = 'ibmq_santiago'
    #backend = 'qasm_simulator'

    # Map virtual qubits to physical qubits
    physicalq0 = 2
    physicalq1 = 3
    physicalq2 = 4

    J = 1
    Bx = 0.2
    dB = 0.001
    Bz_max = 2
    dt_steps = 0.4
    dt = 'dt'
    gamma = 8

    showfig(J, Bx, dB, Bz_max, dt_steps, dt, gamma, 0, provider, backend, physicalq0, physicalq1, physicalq2)
    #showfig(J, Bx, dB, Bz_max, dt_steps, 1, gamma, 0, provider, backend, physicalq0, physicalq1, physicalq2)
    #showfig(J, Bx, dB, Bz_max, dt_steps, 0.5, gamma, 0, provider, backend, physicalq0, physicalq1, physicalq2)

if __name__ == "__main__":
    main()