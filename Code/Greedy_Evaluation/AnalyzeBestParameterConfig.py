from collections import Counter
import pandas as pd
import numpy as np

def analyze_parameters(df_all, n, num_param_comb):
    if num_param_comb not in [1, 2, 3]:
        raise ValueError("num_param_comb muss 1, 2 oder 3 sein.")
    
    # Funktion zur Auswahl der besten n Zeilen jeder Instanz
    def select_top_n(df, n=n):
        sorted_df = df.sort_values(by='Profit', ascending=False)
        top_n = sorted_df.head(n)
        return top_n
    
    # Datenframe für die besten n Zeilen jeder Instanz erstellen
    top_n_each_instance = pd.concat([select_top_n(df_all[df_all['Instanz'] == instanz]) for instanz in df_all['Instanz'].unique()])
    
    # Zählen der Häufigkeit jeder Parameterkombination in den besten n Zeilen jeder Instanz
    parameter_counts = Counter(tuple(row) for row in top_n_each_instance[['MainTaskPlanner', 'AttractivenessFunction', 'a-Wert', 'b-Wert']].values)
    
    # Finden der häufigsten Parameterkombinationen
    most_common_params = parameter_counts.most_common(num_param_comb)
    
    if len(most_common_params) < num_param_comb:
        raise ValueError(f"Es wurden weniger als {num_param_comb} unterschiedliche Parameterkombinationen gefunden.")
    
    best_params = [most_common_params[i][0] for i in range(num_param_comb)]
    
    for i, params in enumerate(best_params, start=1):
        print(f"Beste Parameterkombination {i} insgesamt: {params}")
    
    # Berechnung und Ausgabe der Ergebnisse für jede Instanz basierend auf den besten Parameterkombinationen
    results_per_instance = {}
    percent_diff_total = []
    runtime_total = []

    for instanz in df_all['Instanz'].unique():
        subset = df_all[df_all['Instanz'] == instanz]

        # Profite für die besten Parameterkombinationen
        best_profits = []
        runtimes = []

        for params in best_params:
            param_subset = subset[
                (subset['MainTaskPlanner'] == params[0]) &
                (subset['AttractivenessFunction'] == params[1]) &
                (subset['a-Wert'] == params[2]) &
                (subset['b-Wert'] == params[3])
            ]
            best_profit = param_subset['Profit'].max() if not param_subset.empty else np.nan
            runtime = param_subset['runtime'].sum() if not param_subset.empty else 0

            best_profits.append(best_profit)
            runtimes.append(runtime)

        best_profit_with_best_params = max(best_profits)
        chosen_params = best_params[best_profits.index(best_profit_with_best_params)]

        # Berechnung der prozentualen Abweichung
        best_profit_overall = subset['Profit'].max()
        profit_diff = best_profit_overall - best_profit_with_best_params
        percent_diff = (profit_diff / best_profit_overall) * 100 if best_profit_overall > 0 else 0
        percent_diff_total.append(percent_diff)
        
        total_runtime = sum(runtimes)
        runtime_total.append(total_runtime)
        
        results_per_instance[instanz] = {
            'Chosen Params': chosen_params,
            'Best Profit': best_profit_overall,
            'Profit with Best Params': best_profit_with_best_params,
            'Difference': profit_diff,
            'Percent Difference': percent_diff,
            'Total Runtime': total_runtime
        }

    # Ausgabe der Ergebnisse für jede Instanz
    for instanz, results in results_per_instance.items():
        print(f"{instanz}: Gewählte Parameterkombination: {results['Chosen Params']}, "
              f"Bester Profit: {results['Best Profit']}, "
              f"Profit mit gewählter Parameterkombination: {results['Profit with Best Params']}, "
              f"Unterschied: {results['Difference']}, "
              f"Prozentuale Abweichung: {results['Percent Difference']:.2f}%, "
              f"Gesamtlaufzeit: {results['Total Runtime']}")

    # Durchschnittliche prozentuale Abweichung berechnen
    average_percent_diff = sum(percent_diff_total) / len(percent_diff_total) if percent_diff_total else 0
    average_runtime = sum(runtime_total) / len(runtime_total) if runtime_total else 0

    print(f"Durchschnittliche prozentuale Abweichung über alle Instanzen: {average_percent_diff:.2f}%")
    print(f"Durchschnittliche Gesamtlaufzeit über alle Instanzen: {average_runtime:.2f} sek.")

    # Optional: Erstellen eines DataFrames zur besseren Darstellung der Ergebnisse für jede Instanz
    results_per_instance_df = pd.DataFrame.from_dict(results_per_instance, orient='index')
    results_per_instance_df.reset_index(inplace=True)
    results_per_instance_df.rename(columns={'index': 'Instanz'}, inplace=True)

    print(results_per_instance_df)
    #return results_per_instance_df
    return average_percent_diff, average_runtime