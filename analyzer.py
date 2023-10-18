import pandas as pd
import matplotlib.pyplot as plt


def main():
    annunci = pd.read_csv("annunci_all.csv")

    media_prezzo = annunci["prezzo"].mean()
    print(f"Media prezzo: € {media_prezzo:.2f}")

    mediana_prezzo = annunci["prezzo"].median()
    print(f"Mediana prezzo: € {mediana_prezzo:.2f}")

    derivazione_standard_prezzo = annunci["prezzo"].std()
    print(f"Derivazione standard prezzo: € {derivazione_standard_prezzo:.2f}")

    prezzo_minimo = annunci["prezzo"].min()
    print(f"Prezzo minimo: € {prezzo_minimo:.2f}")

    prezzo_massimo = annunci["prezzo"].max()
    print(f"Prezzo massimo: € {prezzo_massimo:.2f}")

    plt.figure(figsize=(10, 7))

    grouped_by_agenzia = annunci.groupby("agenzia")
    grouped_by_agenzia["prezzo"].mean().plot(kind="bar", title="Media prezzo per agenzia", xlabel="Agenzia",
                                             ylabel="Media prezzo")
    plt.show()


if __name__ == '__main__':
    main()
