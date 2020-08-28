import os
import sys

import matplotlib.pyplot as plt
import numpy as np

"""
Issues: bad files won't normally be used here because you should have a nicely
averaged dataset already. Maybe that's fine. What do I know.
"""
def cycle(dir='./', rel_phase=0, maxQ=0.5):
    if dir[-1] != '/':
        dir += '/'
    rel_phase = rel_phase * np.pi / 180
    filelist = [
        ii for ii in os.listdir(dir)
        if ii.endswith('.txt') and ii.startswith('datafile')
    ]
    filelist.sort()
    filechunks = []

    for file in filelist:
        chunks = file.split('_')
        filechunks.append(chunks)

    dif_list = [False] * len(filechunks[0])
    num_dif = [0] * (len(filechunks) - 1)

    for ii in range(len(filechunks) - 1):
        for kk in range(len(filechunks[0])):
            if filechunks[ii][kk] == filechunks[ii + 1][kk]:
                dif_list[kk] = True
            else:
                dif_list[kk] = False
        num_dif[ii] = len(dif_list) - sum(dif_list)

    num_dif = np.array(num_dif)
    group_dividers = np.where(num_dif != 1)[0]
    group_dividers = np.append(group_dividers, len(filelist) - 1)
    grouplist = []

    start = 0
    Qlist = []
    bad_files = {}

    for elem in group_dividers:
        grouplist.append(filelist[start:elem + 1])
        start = elem + 1

    for group in grouplist:
        for ii in range(len(group[0])):
            if group[0][:ii] not in group[1]:
                writefile = dir + 'cycled' + \
                    group[0][len('datafile'):ii-2] + '.txt'
                phase_idx = ii - 1

                break

        phase_list = [
            int(ii[phase_idx:].split('_')[0].split('.')[0]) for ii in group
        ]
        s = [13000, 13050]
        group = sorted(group, key=lambda x: float(x.split('_')[-1][:-4]))
        phase_list = sorted(phase_list)

        for file in group:
            data = eval(open(dir + file, 'r').read())
            print(file)

            if group.index(file) == 0:
                print("ref file")
                time_domain = np.array(
                    data['Ch1']) + 1j * np.array(data['Ch2'])
                ref_signal = np.copy(
                    time_domain[data['Limits'][0]:data['Limits'][-1]])
                boy0 = np.copy(time_domain[s[0]:s[1]])
            else:
                current_td = np.array(data['Ch1']) + 1j * np.array(data['Ch2'])
                pulse_signal = np.copy(
                    current_td[data['Limits'][0]:data['Limits'][-1]])
                phi = np.angle(np.dot(ref_signal.conjugate(), pulse_signal))
                phase = phase_list[group.index(file)] * np.pi / 180
                # Get angle between two complex vectors -- easy to see using
                # dot product and polar form. When the exponentials all need
                # to be summed, write them as cos and sin and it becomes clear
                # how one can extract the angle.
                phased_td = np.exp(-1j *
                                   (rel_phase + phase + phi)) * current_td
                phased_pulse = np.exp(
                    -1j *
                    (rel_phase +
                     phi)) * pulse_signal  # should match the pulse very well

                Q = np.real(
                    np.dot((phased_pulse.conjugate() - ref_signal.conjugate()),
                           (phased_pulse - ref_signal)) /
                    np.dot(ref_signal.conjugate(), ref_signal))
                Qlist.append(Q)

                if Q > maxQ:
                    bad_files[file] = Q
                else:
                    time_domain += phased_td

                if '90' in file:
                    boy90 = current_td[s[0]:s[1]] * np.exp(-1j * (phi + phase))
                elif '270' in file:
                    boy270 = current_td[s[0]:s[1]] * \
                        np.exp(-1j * (phi + phase))
                elif '180' in file:
                    boy180 = np.copy(current_td[s[0]:s[1]] *
                                     np.exp(-1j * (phi + phase)))

                if phi < 0:
                    phi += 2 * np.pi
                print(
                    f"{int(phase * 180 / np.pi)} plate: {phi * 180 / np.pi:.1f} degree stochastic shift -- Q={Q:.2f}"
                )

        data['Ch1'] = list(np.real(time_domain))
        data['Ch2'] = list(np.imag(time_domain))

        with open(writefile, 'w') as f:
            print(data, file=f)

        print("=" * len(filelist[-1]))

    # print(np.imag(time_domain[s[0]:s[1]]) - np.imag(boy0) + np.imag(boy180))
    # plt.plot(np.real(time_domain[s[0]:s[1]]), label='cycled')
    # plt.plot(np.imag(boy0) + np.imag(boy180), label='0-180', marker='*')
    # plt.plot(np.imag(boy90) + np.imag(boy270), label='90-270', marker='*')
    # plt.plot(np.imag(boy0) + np.imag(boy180) -
    #          (np.imag(boy90) + np.imag(boy270)),
    #          label='dif',
    #          marker='.')
    # plt.plot(np.imag(boy0) + np.imag(boy180) +
    #          (np.imag(boy90) + np.imag(boy270)),
    #          label='sum',
    #          marker='.')
    # plt.plot(np.real(boy90) + np.real(boy270) + np.real(boy0) + np.real(boy180), label='cycle?')
    # plt.plot(np.real(boy0), label='0')
    # plt.plot(np.imag(boy0), label='i0')
    # plt.plot(np.real(boy90), label='90')
    # plt.plot(np.imag(boy90), label='i90')
    # plt.plot(np.real(boy180), label='180')
    # plt.plot(np.imag(boy180), label='i180')
    # plt.plot(np.real(boy270), label='270')
    # plt.plot(np.imag(boy270), label='i270')
    # plt.legend().set_draggable(True)
    # plt.show()
    # dif = np.sum(
    #         np.abs(
    #             np.imag(boy0) + np.imag(boy180) -
    #             (np.imag(boy90) + np.imag(boy270))))
    # su = np.sum(
    #         np.abs(
    #             np.imag(boy0) + np.imag(boy180) +
    #             (np.imag(boy90) + np.imag(boy270))))
    # print(f"dif: {dif}\nsum: {su}")
    
    Qmean = np.mean(np.array(Qlist))
    Qstd = np.std(np.array(Qlist))

    print(f"mean Q: {Qmean:.2f} ------- stdev Q: {Qstd:.2f}\nAn initial choice for Q may be {Qmean + 2*Qstd:.2f}")

    if bad_files:
        print("Bad files:")

    for key in bad_files:
        print(f"{key} ------- Q={bad_files[key]:.2f}")


if __name__ == "__main__":
    cycle(
        dir=
        '/Volumes/GoogleDrive/My Drive/Research/Data/2020-08-05_BDPA_Bz_FELEPR/2020-08-05-T1-single-scan/cycled/test',
        rel_phase=0,
        maxQ=0.59)
