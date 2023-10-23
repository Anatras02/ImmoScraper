from matplotlib import pyplot as plt


def plot_grafico_media_prezzi_nel_tempo(annunci):
    annunci_senza_prezzi_nan = annunci.dropna(subset=["prezzo"], inplace=False).copy()
    annunci_senza_prezzi_nan["media_settimanale"] = annunci_senza_prezzi_nan["prezzo"].rolling(window=7,
                                                                                               min_periods=1).mean()
    annunci_senza_prezzi_nan["media_settimanale"].interpolate(method="linear", inplace=True)
    annunci_senza_prezzi_nan.plot(x='data_ultima_modifica_prezzo', y='media_settimanale')
    plt.show()
