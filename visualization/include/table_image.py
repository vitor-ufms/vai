""" Table from files utils """
from include import Signal
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
import dataframe_image as dfi

def signals_compare_table(signals, dirpath, fn_prefix):
    df = pd.DataFrame()
    filename = dirpath + fn_prefix + "signal_table"
    df['Signals'] = ["R2_array", "R2_pcap"]

    df['Switch_CSV'] = [
        r2_score(signals[0].signal, signals[2].signal), 
        r2_score(signals[0].signal, signals[1].signal)]
    df['PCAP'] = [
        r2_score(signals[1].signal, signals[2].signal),
        r2_score(signals[1].signal, signals[1].signal),]

    df.set_index('Signals')
    
    dfi.export(df, filename)

def dwt_compare_table(signals, type, level, dirpath, fn_prefix):
    columns = ["DWT_" + type, "Switch_CSV", "Switch_lib", "PCAP"]
    df = pd.DataFrame()
    filename = dirpath + fn_prefix + "dwt_" + type + "_table"

    for i in range(1, level + 1):
        for key, name in enumerate(["pcap", "array"]):
            row_name = "R2_" + name + "_lvl" + str(i)
            if (type == "lp"):
                row_df = pd.DataFrame([[row_name,
                    r2_score(signals[0].a_coefficient_csv[i - 1], signals[key + 1].a_coefficient[i - 1]),
                    r2_score(signals[0].a_coefficient[i - 1], signals[key + 1].a_coefficient[i - 1]),
                    r2_score(signals[1].a_coefficient[i - 1], signals[key + 1].a_coefficient[i - 1]),
                ]])
                df = pd.concat([df, row_df], ignore_index=True)
            elif (type == "hp"):
                row_df = pd.DataFrame([[row_name,
                    r2_score(signals[0].d_coefficient_csv[i - 1], signals[key + 1].d_coefficient[i-1]),
                    r2_score(signals[0].d_coefficient[i - 1], signals[key + 1].d_coefficient[i-1]),
                    r2_score(signals[1].d_coefficient[i - 1], signals[key + 1].d_coefficient[i-1]),
                ]])
                df = pd.concat([df, row_df], ignore_index=True)
    df.columns = columns
    df.set_index(columns[0])
    print (df)
    
    dfi.export(df, filename)

def var_compare_table(signals, type, level, dirpath, fn_prefix):
    columns = ["Var_" + type, "Switch_CSV", "Switch_lib", "PCAP"]
    df = pd.DataFrame()
    filename = dirpath + fn_prefix + "var_" + type + "_table"

    for i in range(1, level + 1):
        for key, name in enumerate(["pcap", "array"]):
            row_name = "R2_" + name + "_lvl" + str(i)
            if (type == "lp"):
                row_df = pd.DataFrame([[row_name,
                    r2_score(signals[0].a_variance_csv[i - 1], signals[key + 1].a_variance[i - 1]),
                    r2_score(signals[0].a_variance[i - 1], signals[key + 1].a_variance[i - 1]),
                    r2_score(signals[1].a_variance[i - 1], signals[key + 1].a_variance[i - 1]),
                ]])
                df = pd.concat([df, row_df], ignore_index=True)
            elif (type == "hp"):
                row_df = pd.DataFrame([[row_name,
                    r2_score(signals[0].d_variance_csv[i - 1], signals[key + 1].d_variance[i-1]),
                    r2_score(signals[0].d_variance[i - 1], signals[key + 1].d_variance[i-1]),
                    r2_score(signals[1].d_variance[i - 1], signals[key + 1].d_variance[i-1]),
                ]])
                df = pd.concat([df, row_df], ignore_index=True)
    df.columns = columns
    df.set_index(columns[0])
    print (df)
    
    dfi.export(df, filename)

def var_last_value_compare_table(signals, type, level, dirpath, fn_prefix):
    columns = ["Var_LV_" + type, "Switch_CSV", "Switch_lib", "PCAP", "Array"]
    df = pd.DataFrame()
    filename = dirpath + fn_prefix + "var_lv_" + type + "_table"

    for i in range(1, level + 1):
        row_name = "Lvl" + str(i)
        if (type == "lp"):
            row_df = pd.DataFrame([
                [row_name,
                signals[0].a_variance_last_value_csv[i - 1],
                signals[0].a_variance_last_value[i - 1],
                signals[1].a_variance_last_value[i - 1],
                signals[2].a_variance_last_value[i - 1]
                ]
            ])
            df = pd.concat([df, row_df], ignore_index=True)
        elif (type == "hp"):
            row_df = pd.DataFrame([
                [row_name,
                signals[0].d_variance_last_value_csv[i - 1],
                signals[0].d_variance_last_value[i - 1],
                signals[1].d_variance_last_value[i - 1],
                signals[2].d_variance_last_value[i - 1]
                ]
            ])
            df = pd.concat([df, row_df], ignore_index=True)
    df.columns = columns
    df.set_index(columns[0])
    print (df)
    
    dfi.export(df, filename)

def var_last_value_log_compare_table(signals, type, level, dirpath, fn_prefix):
    columns = ["Var_Log2_" + type, "Switch_CSV", "Switch_lib", "PCAP", "Array"]
    df = pd.DataFrame()
    filename = dirpath + fn_prefix + "var_log2_" + type + "_table"

    for i in range(1, level + 1):
        row_name = "Lvl" + str(i)
        if (type == "lp"):
            row_df = pd.DataFrame([
                [row_name,
                signals[0].a_variance_last_value_log2_csv[i - 1],
                signals[0].a_variance_last_value_log2[i - 1],
                signals[1].a_variance_last_value_log2[i - 1],
                signals[2].a_variance_last_value_log2[i - 1]
                ]
            ])
            df = pd.concat([df, row_df], ignore_index=True)
        elif (type == "hp"):
            row_df = pd.DataFrame([
                [row_name,
                signals[0].d_variance_last_value_log2_csv[i - 1],
                signals[0].d_variance_last_value_log2[i - 1],
                signals[1].d_variance_last_value_log2[i - 1],
                signals[2].d_variance_last_value_log2[i - 1]
                ]
            ])
            df = pd.concat([df, row_df], ignore_index=True)
    df.columns = columns
    df.set_index(columns[0])
    print (df)
    
    dfi.export(df, filename)

def energy_compare_table(signals, level, dirpath, fn_prefix):
    columns = ["Energy", "Switch_CSV", "Switch_lib", "PCAP", "Array"]
    df = pd.DataFrame()
    filename = dirpath + fn_prefix + "energy_table"

    for i in range(1, level + 1):
        row_name = "Lvl" + str(i)
        row_df = pd.DataFrame([
            [row_name,
            signals[0].energy_csv[i - 1],
            signals[0].energy[i - 1],
            signals[1].energy[i - 1],
            signals[2].energy[i - 1]
            ]
        ])
        df = pd.concat([df, row_df], ignore_index=True)
        
    df.columns = columns
    df.set_index(columns[0])
    print (df)
    
    dfi.export(df, filename)
