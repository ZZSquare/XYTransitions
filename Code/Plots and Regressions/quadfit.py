import numpy as np
import matplotlib.pyplot as plt

#data = np.array([[0.03, 0.320566], [0.05, 0.328107], [0.1, 0.354513]])  #lima
#data = np.array([[0.03, 0.253864], [0.05, 0.25784], [0.1, 0.304912]])   #corrected
#data = np.array([[0.03, 0.26511645], [0.05, 0.2767227], [0.1, 0.32600356]])   #corrected2
#data = np.array([[0.03, 0.26579], [0.05, 0.288704], [0.1, 0.337486]])  #santiago
#data = np.array([[0.03, 0.25502], [0.05, 0.276148], [0.1, 0.29834]]) #santiago corrected
#data = np.array([[0.03, 0.260428], [0.05, 0.282913], [0.1, 0.312224]]) #santiago corrected2

fend = ['translated']

#fend = ['scaled', 'translated']
for label in fend:
    file = '413\\regression '+label+'.txt'

    #exact = [[0.03, -0.249098], [0.05, -0.247487], [0.1, -0.239791]]
    exact = [[0.03, 0.249098], [0.05, 0.247487], [0.1, 0.239791]]
    simulated = [[0.03, 0.24411486], [0.05, 0.252], [0.1, 0.26727]]
    colors=['red', 'brown', 'green', 'gray']

    for n in range(4):
        i = 0
        data = []
        posdata = []
        negdata = []
        poserror = []
        negerror = []
        with open(file) as f:
            lines = f.readlines()
            data.append([float(0.03), float(lines[i].split(' ')[n].rstrip())])
            data.append([float(0.05), float(lines[i+3].split(' ')[n].rstrip())])
            data.append([float(0.1), float(lines[i+6].split(' ')[n].rstrip())])
            posdata.append([float(0.03), float(lines[i+1].split(' ')[n].rstrip())])
            posdata.append([float(0.05), float(lines[i+4].split(' ')[n].rstrip())])
            posdata.append([float(0.1), float(lines[i+7].split(' ')[n].rstrip())])
            negdata.append([float(0.03), float(lines[i+2].split(' ')[n].rstrip())])
            negdata.append([float(0.05), float(lines[i+5].split(' ')[n].rstrip())])
            negdata.append([float(0.1), float(lines[i+8].split(' ')[n].rstrip())])

            poserror.append(float(lines[i+2].split(' ')[n].rstrip())-data[0][1])
            poserror.append(float(lines[i+5].split(' ')[n].rstrip())-data[1][1])
            poserror.append(float(lines[i+8].split(' ')[n].rstrip())-data[2][1])

            negerror.append(data[0][1]-float(lines[i+1].split(' ')[n].rstrip()))
            negerror.append(data[1][1]-float(lines[i+4].split(' ')[n].rstrip()))
            negerror.append(data[2][1]-float(lines[i+7].split(' ')[n].rstrip()))


        data = np.array(data)
        posdata = np.array(posdata)
        negdata = np.array(negdata)
        exact = np.array(exact)
        simulated = np.array(simulated)
        error = [negerror, poserror]

        fit = np.polyfit(data[:, 0], data[:, 1], 2)
        line  = np.poly1d(fit)
        posfit = np.polyfit(posdata[:, 0], posdata[:, 1], 2)
        posline  = np.poly1d(posfit)
        negfit = np.polyfit(negdata[:, 0], negdata[:, 1], 2)
        negline  = np.poly1d(negfit)
        exactfit = np.polyfit(exact[:, 0], exact[:, 1], 2)
        exactline  = np.poly1d(exactfit)
        #print(fit)
        print(line(0))
        #print(posline(0))
        #print(negline(0))
        #print(exactline(0))

        #plt.errorbar(data[:, 0], data[:, 1], yerr=error, marker='.', ls='none', label=str(2*n+2)+' points', color=colors[n])
        plt.scatter(data[:, 0], data[:, 1], marker='o', color=colors[n])
        range = np.arange(0, .12, .001)
        plt.plot(range, line(range), color=colors[n])

    plt.scatter(exact[:, 0], exact[:, 1], marker='o', color='grey')
    plt.plot(range, exactline(range), label='exact', linestyle=':', color='grey')
    plt.axhline(y=0.25, color='magenta', linestyle='-.')
    #plt.plot(simulated[:, 0], simulated[:, 1])
    plt.xlabel('$B_x$', fontsize=20)
    plt.ylabel('$B_z$ at Transition', fontsize=20)
    #plt.legend(loc="lower left")
    #plt.text(0.016, 0.2437, '(0, 0.2499)', fontsize=12)
    #plt.arrow(0.02, .245, -0.02, 0.0045, width=0.00024, color='black')
    #plt.legend()
    plt.text(0.01, 0.237, '(0, -0.25)', fontsize=16)
    plt.text(0.07, 0.32, '2 points', color='red', fontsize=18)
    plt.text(0.064, 0.276, '6 points', color='green', fontsize=18)
    plt.text(0.095, 0.298, '8 points', color='grey', fontsize=18)
    plt.text(0.022, 0.289, '4 points', color='brown', fontsize=18)

    plt.xlim(xmin=0)

plt.show()

#plt.savefig('415\\phasetransition.png')