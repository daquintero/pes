from ..types import MultiTimeSignalData


def plot_time_signals(multi_data_time_signal: MultiTimeSignalData):
    """
    TODO signals
    """
    import matplotlib.pyplot as plt

    for data_time_signal_i in multi_data_time_signal:
        plt.plot(data_time_signal_i.time_s, data_time_signal_i.voltage_V)
