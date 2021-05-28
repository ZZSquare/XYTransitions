import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from qiskit.ignis.mitigation.measurement import complete_meas_cal, CompleteMeasFitter
from qiskit import Aer, QuantumRegister, QuantumCircuit, execute, IBMQ, ClassicalRegister, transpile
from negativeqfunctions2spin import adiabaticramp, theta, twospin_instruction, exactm, interactionm
from qiskit.test.mock import FakeVigo, FakeSantiago, FakeProvider


def twospin_df(J, Bx, dB, Bz_max, dt_steps, dt_steps_bool, gamma, skip, provider, backend, pq0, pq1):
    count_list = []
    calibrated_count_list = []
    tarray, Bzarray, dt_or_steps, _ = adiabaticramp(J, Bx, dB, Bz_max, dt_steps, dt_steps_bool, gamma)

    if dt_steps_bool == 'dt':
        dt = dt_steps
    else:
        dt = dt_or_steps

    thetaarray, _ = theta(Bzarray, dt)

    # Calibration Matrix
    calqr = QuantumRegister(2)
    meas_calibs, state_labels = complete_meas_cal(qubit_list=[0, 1], qr=calqr, circlabel='2spin')
    #t_cal = transpile(meas_calibs, FakeSantiago(), initial_layout={calqr[0]:pq0, calqr[1]:pq1})
    #cal_results = execute(t_cal, backend=FakeSantiago(), shots=5000).result()
    t_cal = transpile(meas_calibs, provider.get_backend(backend), initial_layout={calqr[0]:pq0, calqr[1]:pq1})
    cal_results = execute(t_cal, backend=provider.get_backend(backend), shots=5000).result()
    meas_fitter = CompleteMeasFitter(cal_results, state_labels, circlabel='2spin')
    #meas_fitter.plot_calibration()

    i = 0
    while (i < len(thetaarray)):
    #while (i < 6):
        print('Bz = %f' % (Bzarray[i]))
        qr = QuantumRegister(2, 'qr')
        cr = ClassicalRegister(2, 'cr')
        circ = QuantumCircuit(qr, cr)
        #circ.initialize([1, 0, 0, 0], [0, 1])

        twospin_instruction(circ, J, Bx, thetaarray[:i + 1], dt)
        circ.measure([0, 1], [0, 1])

        #t_qc = transpile(circ, FakeSantiago(), initial_layout={qr[0]:pq0, qr[1]:pq1})
        #result = execute(t_qc, FakeSantiago(), shots=5000).result()
        t_qc = transpile(circ, provider.get_backend(backend), initial_layout={qr[0]: pq0, qr[1]: pq1})
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
    df['Exact'] = exactm(J, Bx, Bzarray, dt)
    df['Interaction'] = interactionm(J, Bx, thetaarray, dt)

    calibrated_df = pd.DataFrame(calibrated_count_list)
    time_col = df.pop('Time')
    df.insert(0, 'Time', time_col)

    if '00' not in df:
        df['00'] = 0
    if '01' not in df:
        df['01'] = 0
    if '10' not in df:
        df['10'] = 0
    if '11' not in df:
        df['11'] = 0
    df = df.fillna(0)

    if '00' not in calibrated_df:
        calibrated_df['00'] = 0
    if '01' not in calibrated_df:
        calibrated_df['01'] = 0
    if '10' not in calibrated_df:
        calibrated_df['10'] = 0
    if '11' not in calibrated_df:
        calibrated_df['11'] = 0
    calibrated_df = calibrated_df.fillna(0)

    # Calculating mz
    total = df['00'] + df['01'] + df['10'] + df['11']
    df['mz'] = -(df['00'] / total - df['11'] / total)
    calibrated_df['mz'] = -(df['00'] / total - df['11'] / total)

    # Creating Files
    if dt_steps_bool == 'dt':
        df.to_csv('J={:.3f} Bx={:.3f} dB={:.3f} BzMax={:.3f} dt={:.3f} gamma={:.3f}.csv'.format(J, Bx, dB, Bz_max,
                                                                                                      dt_steps, gamma))
        calibrated_df.to_csv('Calibrated J={:.3f} Bx={:.3f} dB={:.3f} BzMax={:.3f} dt={:.3f} gamma={:.3f}.csv'.format(J, Bx, dB,
                                                                                                            Bz_max,
                                                                                                           dt_steps,
                                                                                                           gamma))
        #df.to_csv('415\QubitTest\%i and %i.csv' %(pq0, pq1))
        #calibrated_df.to_csv('415\QubitTest\Calibrated %i and %i.csv' % (pq0, pq1))
        #df.to_csv('415\FakeSantiago\Bx=%f.csv' %(Bx))
        #calibrated_df.to_csv('415\FakeSantiago\Calibrated Bx=%f.csv' %(Bx))
    else:
        df.to_csv(
            'J={:.3f} Bx={:.3f} dB={:.3f} BzMax={:.3f} BzSteps={:.3f} gamma={:.3f}.csv'.format(J, Bx, dB, Bz_max,
                                                                                                     dt_steps, gamma))
        calibrated_df.to_csv(
            'Calibrated J={:.3f} Bx={:.3f} dB={:.3f} BzMax={:.3f} BzSteps={:.3f} gamma={:.3f}.csv'.format(J, Bx,
                                                                                                                dB,
                                                                                                                Bz_max,
                                                                                                                dt_steps,
                                                                                                                gamma))

    return df, calibrated_df, dt_or_steps, thetaarray


def showfig(J, Bx, dB, Bz_max, dt_steps, dt, gamma, skip, provider, backend, pq0, pq1):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df, calibrated_df, _, thetaarray = twospin_df(J, Bx, dB, Bz_max, dt_steps, dt, gamma, skip, provider, backend, pq0, pq1)

    fig.add_trace(go.Scatter(x=calibrated_df['Bz'], y=calibrated_df['mz'], name='Calibrated', mode='lines+markers'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['mz'], name='Circuit', mode='lines+markers'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Bz'], y=df['Exact'], name='Exact', mode='lines'), secondary_y=False)
    #fig.add_trace(go.Scatter(x=df['Bz'], y=df['Interaction'], name='Interaction', mode='lines'), secondary_y=False)

    # fig.add_trace(go.Scatter(x=df['Bz'], y=thetaarray, name='Theta', mode='markers'), secondary_y=True)
    title = "J=" + str(J) + " Bx=" + str(Bx) + " gamma=" + str(gamma) + " dt_steps=" + str(dt_steps)
    fig.update_layout(title_text=title)
    fig.update_xaxes(title_text="Bz")
    fig.update_yaxes(title_text="mz", secondary_y=False)
    # fig.update_yaxes(title_text="theta", secondary_y=True)
    fig.show()
    #fig.write_html('FakeBelem\\' + title+'.html')
    #fig.write_html('415\QubitTest\%i and %i.html' % (pq0, pq1))
    #fig.write_html('415\\FakeSantiago\\'+title+'.html')

def main():

    # Set account credentials here
    #IBMQ_KEY =
    #IBMQ.save_account(IBMQ_KEY)
    #provider = IBMQ.load_account()
    provider = Aer

    # Set name of backend
    # eg. 'ibmq_santiago'
    backend = 'qasm_simulator'

    # Map virtual qubits to physical qubits
    physicalq0 = 3
    physicalq1 = 4

    J = 1
    Bx = 0.03
    dB = 0.01
    Bz_max = 2
    dt_steps = 2
    dt = 'dt'
    gamma = 3

    showfig(J, 0.03, dB, Bz_max, 2, dt, 3, 0, provider, backend, physicalq0, physicalq1)
    showfig(J, 0.05, dB, Bz_max, 1.6, dt, 4, 0, provider, backend, physicalq0, physicalq1)
    showfig(J, 0.1, dB, Bz_max, 0.9, dt, 5, 0, provider, backend, physicalq0, physicalq1)

    #showfig(J, 0.03, dB, Bz_max, 2, dt, 3, 0, provider, backend, 0, 1)
    #showfig(J, 0.03, dB, Bz_max, 2, dt, 3, 0, provider, backend, 1, 2)
    #showfig(J, 0.03, dB, Bz_max, 2, dt, 3, 0, provider, backend, 2, 3)
    #showfig(J, 0.03, dB, Bz_max, 2, dt, 3, 0, provider, backend, 3, 4)


if __name__ == "__main__":
    main()