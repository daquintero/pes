# # Digital Simulation & Layout Design Space Exploration

# ### Deployment and Timing of Large-Scale `openlane 2`
#
# One common and powerful aspect of this tool is the large-scale deployment of `openlane 2` designs so you can explore, say, the effect of different variations on your digital designs. You might want to multi-thread running your designs. Let's explore how to do this.
#
# We will use the built-in `multiprocessing` module in `python`:

import multiprocessing
import time
import piel

# We will go through the whole process of using `amaranth` for digital simulation and design later. For now, let's assume we have a random truth table we want to implement multiple times with different `id`. We will time both sequential and parallel implementations of this layout flow, and determine which is faster.

from piel.integration.amaranth_openlane import layout_truth_table_through_openlane

truth_table_dictionary = truth_table = {
    "input": [
        "0000",
        "0001",
        "0010",
        "0011",
        "0100",
        "0101",
        "0110",
        "0111",
        "1000",
        "1001",
        "1010",
        "1011",
        "1100",
        "1101",
        "1110",
        "1111",
    ],
    "output": [
        "0101",
        "1100",
        "0101",
        "0110",
        "0010",
        "1101",
        "0110",
        "0011",
        "1001",
        "1110",
        "0100",
        "1000",
        "0001",
        "1011",
        "1111",
        "1010",
    ],
}
input_ports_list = ["input"]
output_ports_list = ["output"]
truth_table = piel.types.TruthTable(
    input_ports=input_ports_list,
    output_ports=output_ports_list,
    **truth_table_dictionary,
)
truth_table.dataframe


#
# |    |   input |   output |
# |---:|--------:|---------:|
# |  0 |    0000 |     0101 |
# |  1 |    0001 |     1100 |
# |  2 |    0010 |     0101 |
# |  3 |    0011 |     0110 |
# |  4 |    0100 |     0010 |
# |  5 |    0101 |     1101 |
# |  6 |    0110 |     0110 |
# |  7 |    0111 |     0011 |
# |  8 |    1000 |     1001 |
# |  9 |    1001 |     1110 |
# | 10 |    1010 |     0100 |
# | 11 |    1011 |     1000 |
# | 12 |    1100 |     0001 |
# | 13 |    1101 |     1011 |
# | 14 |    1110 |     1111 |
# | 15 |    1111 |     1010 |


# ### Verify Our Environment Configuration

# This should run successfully for the remaining example

layout_truth_table_through_openlane

layout_truth_table_through_openlane(
    truth_table=truth_table,
    parent_directory="sequential",
    target_directory_name="sequential_test",
)


# ### Configure Optimised Runs


def sequential_implementations(amount_of_implementations: int):
    implementations = list()

    for i in range(amount_of_implementations):
        implementation_i = layout_truth_table_through_openlane(
            truth_table=truth_table,
            parent_directory="sequential",
            target_directory_name="sequential_" + str(i),
        )
        implementations.append(implementation_i)


def parallel_implementations(amount_of_implementations: int):
    processes = []

    for i in range(amount_of_implementations):
        # Create all processes
        process_i = multiprocessing.Process(
            target=layout_truth_table_through_openlane,
            kwargs={
                "truth_table": truth_table,
                "parent_directory": "parallel",
                "target_directory_name": "parallel_" + str(i),
            },
        )
        processes.append(process_i)

    for p in processes:
        p.start()

    # This starts them in parallel
    for p in processes:
        p.join()


# Let's time this:

# +
start_sequential = time.time()
sequential_implementations(amount_of_implementations=4)
end_sequential = time.time()

print("Sequential")
print(end_sequential - start_sequential)
# -
# ```
# Sequential
# 106.13592076301575
# ```

# +
start_parallel = time.time()
parallel_implementations(amount_of_implementations=4)
end_parallel = time.time()

print("Parallel")
print(end_parallel - start_parallel)
# -

# ```python
# Parallel
# 42.47045159339905
# ```
