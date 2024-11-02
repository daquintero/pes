# # RF Amplifier Design & Analysis Flow

# In this example, we will understand the design, modelling and performance requirements of an RF amplifier. We will specifically explore ultra-wideband ~180nm CMOS designs as these are more reproducible with open-source toolsets and relevant to some photonics-compatible loads.
#
# We will first understand performance parameters of a set of ultra-wideband designs before using this as reference to model a similar design using open-source technology and `piel`.

import piel
import piel.experimental as pe
import os

# ## Basic Terminology
#
# Let's start by understanding basic terminology of our amplification range.
#
# Let's first consider the relationship between DC and RF time-and-frequency units in terms of representing the power. Say we are considering signal sources such as a [SynthHD](https://windfreaktech.com/product/microwave-signal-generator-synthhd/).

# ### Power Conversion Functionality

# Let's consider some power conversion tools which are very common when talking about amplifiers:

# If we want to convert from $dBm$ to $W$:
#
# \begin{equation}
# P_{\text{dBm}} = 10 \times \log_{10}\left(\frac{P_{\text{Watt}}}{10^{-3}}\right)
# \end{equation}
#
# and backwards:
#
# \begin{equation}
# P_{\text{Watt}} = 10^{\left(\frac{P_{\text{dBm}}}{10}\right)} \times 10^{-3}
# \end{equation}
#

# We can use this functionality from `piel`:

piel.units.dBm2watt(30)

piel.units.watt2dBm(1)

# Now, normally in RF systems we consider things in terms of network impedance as this is in relation to our waveguides and matching loads. We might want to know what is the peak-to-peak voltage of each of our loads accordingly.

# You might want to work out what the peak-to-peak voltage is for a 50 $\Omega$ load for a given decibel-milliwatt measurement:

piel.units.dBm2vpp(1, impedance=50)

piel.units.dBm2vpp(10)

# Or convert backwards from a given $dBm$:

piel.units.vpp2dBm(2)

# ### Relationship to Signal Metrics

# We will explore the performance of a SynthHD (v2): 10MHz – 15GHz Dual Channel Microwave RF Signal Generator in this context.
#
# > Tune any frequency between 10MHz and 15GHz in 0.1Hz resolution. Adjust calibrated amplitude in 0.1dB resolution up to +20dBm and across more than 50dB of range
#
# So the maximum this can output is:

piel.units.dBm2vpp(dBm=20)

# ```
# 6.324555320336759
# ```

# If it has 50dB of range then the minimum power output may be around -30dBm:

piel.units.dBm2vpp(dBm=-30)

# ```
# 0.02
# ```

# Note that sometimes it's hard to keep track of units when dealing with multi-physical systems. There are some type operations that are supported within `piel` to streamline this. For example, when speaking of optical power spectral density we define it in units of `dBm/nm`

piel.types.dBm / piel.types.nm

# ## Design Principles
#
# ### From a Basic DC Amplfier Context
#
# A small subset RF amplifiers have a bandwidth starting from DC as this is topology dependent, and many are narrowband or at a specific bandwidth. It can be useful to illustrate some RF amplifier concepts to the radio-frequency terminology uninitated by understanding the relationships to the terminology to used to commonly describe DC amplifiers.
#
# For example, DC amplifiers such as non-inverting operational amplifier circuits, will have a DC transfer function which maps the gain from inputs to outputs. This gain is frequency dependent and becomes more important in RF regimes, and is characterized differently accordingly using a VNA for example. For now, let's demonstrate some basic DC sweep analysis of a DC amplifier using some `piel` utilities.
#
# #### Dummy DC Data
# Creating dummy data in order to demonstrate some linearity analysis:


# +
import numpy as np
import pandas as pd


# Create a sigmoid function for curvilinear behavior
def sigmoid(x, x0, k):
    return 1 / (1 + np.exp(-k * (x - x0)))


for k_i in [25, 100]:
    # Generate a range of voltages for driver_a_v and corresponding measurements
    n_points = 100
    driver_a_v = np.linspace(0, 1, n_points)  # Input voltage from 0 to 1V
    measurement_a_v = sigmoid(driver_a_v, x0=0.5, k=k_i)  # Sigmoid curve

    # Create a sample dataset with other values constant as in the original example
    data = {
        "index": range(n_points),
        "driver_a_v": driver_a_v,
        "driver_a_i": np.logspace(1e-10, 1e-5, n_points),  # Simulated current
        "measurement_a_v": measurement_a_v,
        "driver_b_v": np.linspace(
            0.0004, 1.0, n_points
        ),  # Example range for driver_b_v
        "driver_b_i": np.logspace(
            1e-10, 1e-5, n_points
        ),  # Simulated current for driver_b
        "time": pd.date_range(start="2024-07-19 16:40:49", periods=n_points, freq="S"),
        "driver_a_v_set": driver_a_v,
        "driver_a_i_set": np.nan,
        "driver_b_v_set": [3.1] * n_points,
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    csv_path = f"./data/example_dc_response_k{k_i}.csv"
    df.to_csv(csv_path, index=False)
# -

# #### Analysis

# +
dc_sweep_k25 = pe.extract_dc_sweeps_from_operating_point_csv(
    file_path="data/example_dc_response_k25.csv",
    input_signal_name_list=[
        ("driver_a_v", "driver_a_i"),
    ],
    output_signal_name_list=["measurement_a_v"],
    power_signal_name_list=[
        ("driver_b_v", "driver_b_i"),
    ],
    unique_operating_point_columns=["driver_b_v_set"],
)

dc_sweep_k100 = pe.extract_dc_sweeps_from_operating_point_csv(
    file_path="data/example_dc_response_k100.csv",
    input_signal_name_list=[
        ("driver_a_v", "driver_a_i"),
    ],
    output_signal_name_list=["measurement_a_v"],
    power_signal_name_list=[
        ("driver_b_v", "driver_b_i"),
    ],
    unique_operating_point_columns=["driver_b_v_set"],
)

# +
# dc_sweep.collection[0]

# +
fig, axs = (
    piel.visual.experimental.dc.measurement_data_collection.plot_two_port_dc_sweep(
        dc_sweep_k25,
        title="Example DC Sigmoid Response",
        label_list=[r"$k$=25"],
    )
)

fig, axs = (
    piel.visual.experimental.dc.measurement_data_collection.plot_two_port_dc_sweep(
        dc_sweep_k100,
        title="Example DC Sigmoid Response",
        fig=fig,
        axs=axs,
        label_list=[r"$k$=100"],
        path="../../_static/img/examples/09a_model_rf_amplifier/example_dc_sigmoid_response.png",
    )
)
# -

# ![example_dc_sigmoid_response](../../_static/img/examples/09a_model_rf_amplifier/example_dc_sigmoid_response.png)

# One of the complexitites of DC signal analysis, is that sometimes, some of these analogue responses may be dependent on multiple bias references. It is possible to perform DC analysis of the transmission of the entire system accordingly and create a big design space. This is also a good application for machine learning in tuning multiple control points. In our case, we will explore some DC signal analysis just between our reference $v_{in}$ and $V_{out}$


# We can for example begin analysing specific aspects of the signals:

dc_sweep_k25.collection[0].power[0]

power_voltage_array = piel.analysis.signals.dc.get_trace_values_by_datum(
    dc_sweep_k25.collection[0].power[0], "voltage"
)
power_current_array = piel.analysis.signals.dc.get_trace_values_by_datum(
    dc_sweep_k25.collection[0].power[0], "ampere"
)
power_array_W = power_voltage_array * power_current_array
power_array_W

# Let's calculate the maximum DC amplitude and threshold voltage range:

piel.analysis.signals.dc.get_out_min_max(dc_sweep_k25.collection[0]).table

# |    | Metric             |         Value |
# |---:|:-------------------|--------------:|
# |  0 | Value              | nan           |
# |  1 | Mean               | nan           |
# |  2 | Min                |   4.65588e-05 |
# |  3 | Max                |   0.999953    |
# |  4 | Standard Deviation | nan           |
# |  5 | Count              | nan           |

piel.analysis.signals.dc.get_out_response_in_transition_range(
    dc_sweep_k25.collection[0]
).table

# |    | Metric             |      Value |
# |---:|:-------------------|-----------:|
# |  0 | Value              | nan        |
# |  1 | Mean               | nan        |
# |  2 | Min                |   0.414141 |
# |  3 | Max                |   0.585859 |
# |  4 | Standard Deviation | nan        |
# |  5 | Count              | nan        |

# Note that this can be pretty handy in determining DC biases of some amplifiers.

# Another important metric is understanding the DC power consumption of the system. We can generally estimate this by calculate the total $VI$ power consumed within the system.

dc_sweep_k25.collection[0].power

piel.analysis.signals.dc.get_power_metrics(dc_sweep_k25.collection[0]).table

# |    | Metric             |      Value |
# |---:|:-------------------|-----------:|
# |  0 | Value              |   0.500208 |
# |  1 | Mean               |   0.500208 |
# |  2 | Min                |   0.0004   |
# |  3 | Max                |   1.00002  |
# |  4 | Standard Deviation |   0.291467 |
# |  5 | Count              | 100        |

# Note that this is dummy generated data of a logspace and does not aim to represent anything physical. We can also see how these minimum and maximum values map to an input voltage relationship.

piel.analysis.signals.dc.get_power_map_vin_metrics(dc_sweep_k25.collection[0]).table

# Note we might have multiple curves, so we might want to make a table with metrics from multiple signal collections:

piel.analysis.signals.dc.compile_dc_min_max_metrics_from_dc_collection(
    [
        dc_sweep_k25.collection[0],
        dc_sweep_k100.collection[0],
    ],
    label_list=[r"$k$=25", r"$k$=100"],
    label_column_name="ID",
)

# |    | ID      |   $V_{out, min}$ $V$ |   $V_{out, max}$ $V$ |   $V_{tr,in, min}$ $V$ |   $V_{tr,in, max}$ $V$ |   $P_{dd,max}$ $mW$ |   $\Delta P_{dd}$ $mW$ |
# |---:|:--------|---------------------:|---------------------:|-----------------------:|-----------------------:|--------------------:|-----------------------:|
# |  0 | $k$=25  |          4.65588e-05 |             0.999953 |               0.414141 |               0.585859 |             1000.02 |                999.623 |
# |  1 | $k$=100 |          4.6999e-18  |             1        |               0.484848 |               0.515152 |             1000.02 |                999.623 |
#

# ### RF Amplifier Design Context

# When we went through the DC example, we saw how we could apply DC input energy (through voltage and current) and would get a DC output transmission (again through voltage and current).
#
# In RF, especially when we think about amplifiers, we are also thinking about this in these terms. We are putting some input power ($P_{in}$) and getting an output power transmission ($P_{out}$). However, one thing we need to be aware of is that the power transmission is frequency-dependent too, and hence gain and etc. is frequency-dependent too. The relationship between powers leads to $S_{xx}$ parameter port relationships. Normally, one thing we do try to maintain is the proportionality of the voltage and current for a given network impedance ~ normally $50 \Omega$ (in optics this is equivalent to mode matching in an optical waveguide). This leads to some really interesting effects and properties which we will explore further, especially because at RF frequencies there is a lot of harmonic interactions - which are less present in optical frequencies.

# #### Example RF Power Sweep Response

# You might want to refer to how this has been discussed and approached within `scikit-rf`: [this](https://github.com/scikit-rf/scikit-rf/issues/432) and [this](https://github.com/scikit-rf/scikit-rf/issues/903) issue. In the interest of maximizing compatibility of this data with, say electro-optic modulator optical-transmission simulations, it makes sense to boil down the fundamental data inherent to a measurement since it does not seem supported by scikit-rf.
#
# We will extract a non-standard `.s2p` file that contains a power sweep, which was generated from a VNA.

power_sweep_frequency_array_state = pe.extract_power_sweep_s2p_to_network_transmission(
    file_path="data/example_power_sweep_touchstone.s2p",
    input_frequency_Hz=0.5e6,
)

pe.extract_power_sweep_s2p_to_network_transmission

piel.visual.plot.signals.frequency.plot_s21_gain_per_input_power_dBm(
    network_transmission=power_sweep_frequency_array_state,
    path="../../_static/img/examples/09a_model_rf_amplifier/example_power_sweep_plot.png",
)

# ![example_power_sweep_plot](../../_static/img/examples/09a_model_rf_amplifier/example_power_sweep_plot.png)

# There are multiple ways to define a `Transmission` and `Phasor` relationship that represent the frequency-domain response. There are some functions in `piel.analysis.signals.frequency` that allow you to convert between multiple types. Each might have an application depending on the computational complexity of the operations to be performed on it.

two_port_network_transmission_dataframe = (
    piel.analysis.signals.frequency.extract_two_port_network_transmission_to_dataframe(
        power_sweep_frequency_array_state
    )
)
two_port_network_transmission_dataframe
# print(two_port_network_transmission_dataframe.head().to_markdown())

# |    |   magnitude_dBm |   phase_degree |   frequency_Hz |   s_11_magnitude_dBm |   s_11_phase_degree |   s_11_frequency_Hz |   s_21_magnitude_dBm |   s_21_phase_degree |   s_21_frequency_Hz |   s_12_magnitude_dBm |   s_12_phase_degree |   s_12_frequency_Hz |   s_22_magnitude_dBm |   s_22_phase_degree |   s_22_frequency_Hz |
# |---:|----------------:|---------------:|---------------:|---------------------:|--------------------:|--------------------:|---------------------:|--------------------:|--------------------:|---------------------:|--------------------:|--------------------:|---------------------:|--------------------:|--------------------:|
# |  0 |       -10       |              0 |         500000 |             -9.52587 |             173.902 |              500000 |             -40.9485 |            -175.317 |              500000 |             -42.8073 |             161.842 |              500000 |             -16.1038 |             152.356 |              500000 |
# |  1 |        -9.99766 |              0 |         500000 |             -9.48725 |             174.575 |              500000 |             -41.225  |            -173.812 |              500000 |             -43.108  |             162.236 |              500000 |             -16.0967 |             152.018 |              500000 |
# |  2 |        -9.99531 |              0 |         500000 |             -9.5365  |             174.119 |              500000 |             -41.1954 |            -173.292 |              500000 |             -42.4291 |             160.937 |              500000 |             -16.1171 |             152.117 |              500000 |
# |  3 |        -9.99297 |              0 |         500000 |             -9.4748  |             174.517 |              500000 |             -41.0605 |            -177.236 |              500000 |             -42.8502 |             161.739 |              500000 |             -16.0894 |             152.221 |              500000 |
# |  4 |        -9.99062 |              0 |         500000 |             -9.50937 |             174.016 |              500000 |             -41.3541 |            -174.734 |              500000 |             -42.8737 |             163.529 |              500000 |             -16.096  |             152.14  |              500000 |
# ....
#

# Now we have this information in a dataframe, we can use this to perform some device analysis accordingly. Maybe we might want to convert it to an `xarray` dataframe easily for example for higher-dimensional analysis.

# A few things we might want to do is determine the `s_21_dB` maximum gain at the corresponding power input input. Hence, we might want to index the dataframe accordingly for this. We might also want to create a `FrequencyMetric` that contains both transmission and input information given the directional nature. We can also do the analysis directly from the dataframe. However, there are cases where we might be generating multiple frequency-domain data types and need to convert accordingly. As such, it is handy to have static data type operations that enable this analysis on a larger well-defined scale.

maximum_power_transmission_metric = (
    piel.analysis.signals.frequency.max_power_s21_frequency_metric_from_dataframe(
        two_port_network_transmission_dataframe
    )
)
maximum_power_transmission_metric.table

import matplotlib.pyplot as plt

plt.plot(
    two_port_network_transmission_dataframe.magnitude_dBm,
    two_port_network_transmission_dataframe.s_21_magnitude_dBm,
)

# Part of the issue is the 2D nature of our screens and the way we represent data currently. Maybe AR will change that, for now we have to consider concatenating metrics together in the same dimensions of a 2D array. This is, however, quite useful in performing system analysis and relating this to a larger scale network.

# Say we have a collection of these power-sweeps, we probably want to perform analysis on all of them whilst managing the metadata accordingly.


# ## Automated Performance Metrics Analysis

# `piel` provides multiple analysis functionality in order to compare the metrics of different types of published designs. In this case, we will look into designs in the range of the current open-source EIC technologies. In this case, we will construct and visualise multiple design metrics together. Let's do a little literature review for reference which has already been saved in a parse-able-json as below.

# ### ~180nm Low-Noise Amplifier Metrics Analysis

# Let's assume we have a dataset. You can see how to automate generating one in `regenerate_reference_dataframe.py`. Note you can use any json-generation functionality with a compatible schema.

lna_180nm_metrics = piel.read_json("data/lna_180nm_metrics.json")

# We want to load this into a collection object so that we can do more straightforward analysis:

lna_180nm_collection = piel.types.RFAmplifierCollection.parse_obj(lna_180nm_metrics)
# lna_180nm_collection

# We might want to do some analytics with this amplifier collection:

lna_180nm_performance_table = (
    piel.analysis.electronic.compose_amplifier_collection_performance_dataframe(
        amplifier_collection=lna_180nm_collection,
        desired_metrics=["bandwidth_Hz", "power_gain_dB", "power_consumption_mW"],
    )
)
lna_180nm_performance_table

# |    | name   |   bandwidth_Hz_min |   bandwidth_Hz_max |   power_gain_dB_min |   power_gain_dB_max |   power_consumption_mW_min |   power_consumption_mW_max |
# |---:|:-------|-------------------:|-------------------:|--------------------:|--------------------:|---------------------------:|---------------------------:|
# |  0 |        |            4e+08   |            1e+10   |               11.2  |               12.4  |                      12    |                      12    |
# |  1 |        |            5e+08   |            1.4e+10 |               10.6  |               10.6  |                      52    |                      52    |
# |  2 |        |            1e+08   |            7e+09   |               12.6  |               12.6  |                       0.75 |                       0.75 |
# |  3 |        |            5.7e+09 |            5.7e+09 |               11.45 |               11.45 |                       4    |                       4    |

# We can also quite easily generate a metrics table which could be used in a larger `TeX` document:

lna_180nm_performance_table_tex = piel.visual.table.electronic.compose_amplifier_collection_performance_latex_table(
    amplifier_collection=lna_180nm_collection,
    desired_metrics=["bandwidth_Hz", "power_gain_dB", "power_consumption_mW"],
    caption="Compiled electronic performance available from the best CMOS LNA and PA literature for successful low-noise and power amplification.",
    label="table:amplifier_designs_review",
)
piel.write_file(
    directory_path=os.getenv("TAT"),
    file_text=lna_180nm_performance_table_tex,
    file_name="lna_180nm_metrics_analysis.tex",
)
print(lna_180nm_performance_table_tex)

# ```tex
# \begin{center}
#   \begin{table}[h!]
#       \centering
#       \makebox[\textwidth]{%
#           \begin{tabularx}{0.9\paperwidth}{
# |>{\raggedright\arraybackslash\hsize=\hsize}X|X|X|X|
#           }
#           \hline
#            & \textbf{Bandwidth} (GHz) & \textbf{Power Gain} (dB) & \textbf{Power} (mW) \\
# \hline
# \cite{chen2007ultra} & 0.40 - 10.00 & 11.20 - 12.40 & 12.00 \\
# \hline
# \cite{liu20030} & 0.50 - 14.00 & 10.60 & 52.00 \\
# \hline
# \cite{parvizi2014sub} & 0.10 - 7.00 & 12.60 & 0.75 \\
# \hline
# \cite{asgaran20064} & 5.70 & 11.45 & 4.00 \\
# \hline
#       \end{tabularx}%
#       }
#       \caption{Compiled electronic performance available from the best CMOS LNA and PA literature for successful low-noise and power amplification.}
#       \label{table:amplifier_designs_review}
#   \end{table}
# \end{center}
#
#
# ```

# The power of this API is that now we can programmatically perform analysis on literature designs, and use their performance metrics in a larger system we might want to design. This also means we can compare our own designs in relation to the literature much more straightforwardly. The further benefit of this is that if you are doing a literature review, you can input the analysis data into one data container, and use it for both programmatic analysis and making comparison tables.

# For example, we can now perform visual plots of the parametric performance accordingly in order to provide a level of comparison:

# ### ~180nm Power Amplifier Metrics Analysis

# Let's also look into published power amplifier metrics accordingly:
