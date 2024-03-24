import csv
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt


def importVicon(file, export=False, export_path="./vicon.csv", print_df=True):
    blank_row = []

    with open(file, "r") as csvfile:
        datareader = csv.reader(csvfile)
        cnt = 0
        for idx, row in enumerate(datareader):
            if len(row) == 0:
                blank_row.append(idx)
            elif row[0] == "":
                blank_row.append(idx)
            cnt = idx
        blank_row.append(cnt)

    # print(blank_row)

    fp_name_row = blank_row[0]
    fp_start_row = blank_row[1] + 1
    seperate_row = blank_row[2]

    vc_name_row = blank_row[3]
    vc_start_row = blank_row[4] + 1

    fp_header_list = []
    vc_header_list = []
    fp_freq = 0
    vc_freq = 0

    with open(file, "r") as csvfile:
        datareader = csv.reader(csvfile)
        for idx, row in enumerate(datareader):
            if idx == 1:
                fp_freq = row[0]
            if idx == seperate_row + 2:
                vc_freq = row[0]

            if idx == fp_name_row:
                prefix_list = []
                for i in range(4):
                    idx_ = i * 9 + 2
                    s_ = row[idx_].split(" - ")
                    prefix_list.append(s_[0])

                # for i in range(len(row)):
                for i in range(2 + 9 * 4):
                    suffix_list = ["Fx", "Fy", "Fz", "Mx", "My", "Mz", "Cx", "Cy", "Cz"]
                    # print(i, int((i - 2) / 9))
                    if i == 0:
                        header = "frame"
                    elif i == 1:
                        header = "subframe"
                    else:
                        header = (
                            prefix_list[int((i - 2) / 9)]
                            + "_"
                            + suffix_list[(i - 2) % 9]
                        )
                    fp_header_list.append(header)
                # print(fp_header_list)

            if idx == vc_name_row:
                prefix_list = []
                suffix_list = []
                i = 2
                while i < len(row):
                    if row[i] != "":
                        s_ = row[i].split(":")
                        prefix_list.append(s_[1])
                    else:
                        break
                    i += 3
                for i in range(len(row)):
                    suffix_list = ["x", "y", "z"]
                    if i < (len(prefix_list) * 3 + 2):
                        if i == 0:
                            header = "frame"
                        elif i == 1:
                            header = "subframe"
                        else:
                            header = (
                                prefix_list[int((i - 2) / 3)]
                                + "_"
                                + suffix_list[(i - 2) % 3]
                            )
                        vc_header_list.append(header)
                # print(vc_header_list)

    df_fp = pd.read_csv(
        file, skiprows=lambda x: x not in range(fp_start_row, seperate_row), header=None
    )
    df_fp.columns = fp_header_list

    vc_fact = int(float(fp_freq) / float(vc_freq))

    df_vc = pd.read_csv(
        file,
        skiprows=lambda x: x not in range(vc_start_row, blank_row[-1] + 1),
        header=None,
    )
    df_vc = df_vc.drop(labels=list(range(len(vc_header_list), df_vc.shape[1])), axis=1)
    df_vc.columns = vc_header_list

    df_vc_dupl = pd.DataFrame()
    for i in range(df_vc.shape[0]):
        r = df_vc.loc[i].copy()
        df_vc_dupl = df_vc_dupl._append([r] * int(vc_fact), ignore_index=True)

    df_all = pd.concat([df_fp, df_vc_dupl], axis=1).reindex(df_fp.index)

    if export:
        print("file exported to", export_path)
        df_all.to_csv(export_path, index=False)
    if print_df:
        print(df_all)
    return df_all


if __name__ == "__main__":
    argc = len(sys.argv)
    file = ""
    if argc == 3:
        if sys.argv[1] == "-f":
            file = sys.argv[2]
    print("file import: ", file)
    vdf = importVicon(file, export=True)
    plt.plot(np.array(vdf["ForcePlate1_Fz"]))
    plt.plot(np.array(vdf["ForcePlate1_Fx"]))
    plt.show()
