# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
import cocotb
from cocotb.triggers import Timer
from cocotb.utils import get_sim_time
import pandas as pd


@cocotb.test()
async def truth_table_test(dut):
    """Test for logic defined by the truth table"""

    input_fock_state_str_data = []
    bit_phase_0_data = []
    bit_phase_1_data = []
    time = []

    # Test case 1
    dut.input_fock_state_str.value = cocotb.binary.BinaryValue("100")
    await Timer(2, units="ns")

    assert (
        dut.bit_phase_0.value == cocotb.binary.BinaryValue("00000")
    ), f"Test failed for inputs ['input_fock_state_str']: expected 00000 but got {dut.bit_phase_0.value}."
    assert (
        dut.bit_phase_1.value == cocotb.binary.BinaryValue("00000")
    ), f"Test failed for inputs ['input_fock_state_str']: expected 00000 but got {dut.bit_phase_1.value}."
    input_fock_state_str_data.append(dut.input_fock_state_str.value)
    bit_phase_0_data.append(dut.bit_phase_0.value)
    bit_phase_1_data.append(dut.bit_phase_1.value)
    time.append(get_sim_time())

    # Test case 2
    dut.input_fock_state_str.value = cocotb.binary.BinaryValue("001")
    await Timer(2, units="ns")

    assert (
        dut.bit_phase_0.value == cocotb.binary.BinaryValue("00000")
    ), f"Test failed for inputs ['input_fock_state_str']: expected 00000 but got {dut.bit_phase_0.value}."
    assert (
        dut.bit_phase_1.value == cocotb.binary.BinaryValue("11111")
    ), f"Test failed for inputs ['input_fock_state_str']: expected 11111 but got {dut.bit_phase_1.value}."
    input_fock_state_str_data.append(dut.input_fock_state_str.value)
    bit_phase_0_data.append(dut.bit_phase_0.value)
    bit_phase_1_data.append(dut.bit_phase_1.value)
    time.append(get_sim_time())

    # Test case 3
    dut.input_fock_state_str.value = cocotb.binary.BinaryValue("010")
    await Timer(2, units="ns")

    assert (
        dut.bit_phase_0.value == cocotb.binary.BinaryValue("11111")
    ), f"Test failed for inputs ['input_fock_state_str']: expected 11111 but got {dut.bit_phase_0.value}."
    assert (
        dut.bit_phase_1.value == cocotb.binary.BinaryValue("00000")
    ), f"Test failed for inputs ['input_fock_state_str']: expected 00000 but got {dut.bit_phase_1.value}."
    input_fock_state_str_data.append(dut.input_fock_state_str.value)
    bit_phase_0_data.append(dut.bit_phase_0.value)
    bit_phase_1_data.append(dut.bit_phase_1.value)
    time.append(get_sim_time())

    simulation_data = {
        "input_fock_state_str": input_fock_state_str_data,
        "bit_phase_0": bit_phase_0_data,
        "bit_phase_1": bit_phase_1_data,
        "time": time,
    }

    pd.DataFrame(simulation_data).to_csv(
        "/home/daquintero/phd/piel/docs/examples/07_full_flow_demo_electronic_photonic/full_flow_demo/full_flow_demo/tb/out/truth_table_test_results.csv"
    )
