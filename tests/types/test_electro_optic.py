import pytest
import pandas as pd
from piel.types import (
    OpticalStateTransitionCollection,
    # FockStatePhaseTransition,
    # PhaseTransitionTypes,
)  # Adjust the import based on your actual module structure

# Sample files for testing
sample_transmission_data = [
    {
        "phase": (0.5, 1.0),
        "input_fock_state": (1, 0),
        "output_fock_state": (0, 1),
        "target_mode_output": 1,
    },
    {
        "phase": (1.5, 2.0),
        "input_fock_state": (0, 1),
        "output_fock_state": (1, 0),
        "target_mode_output": 0,
    },
]


# Test cases for initialization and attribute verification
def test_optical_state_transitions_initialization():
    model = OpticalStateTransitionCollection(
        mode_amount=2, target_mode_index=1, transmission_data=sample_transmission_data
    )
    assert model.mode_amount == 2
    assert model.target_mode_index == 1
    assert model.transmission_data == sample_transmission_data


def test_optical_state_transitions_dataframe():
    model = OpticalStateTransitionCollection(
        mode_amount=2, target_mode_index=1, transmission_data=sample_transmission_data
    )
    df = model.dataframe
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 4)  # Two rows and four columns
    assert "phase" in df.columns
    assert "input_fock_state" in df.columns
    assert "output_fock_state" in df.columns
    assert "target_mode_output" in df.columns


def test_optical_state_transitions_keys_list():
    model = OpticalStateTransitionCollection(
        mode_amount=2, target_mode_index=1, transmission_data=sample_transmission_data
    )
    keys = model.keys_list
    expected_keys = [
        "phase",
        "input_fock_state",
        "output_fock_state",
        "target_mode_output",
    ]
    assert keys == expected_keys


def test_optical_state_transitions_transition_dataframe():
    model = OpticalStateTransitionCollection(
        mode_amount=2, target_mode_index=1, transmission_data=sample_transmission_data
    )
    df = model.transition_dataframe
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 4)  # Two rows and four columns
    # Check if the specified keys 'unitary' and 'raw_output' are excluded
    assert "unitary" not in df.columns
    assert "raw_output" not in df.columns


def test_optical_state_transitions_target_output_dataframe():
    model = OpticalStateTransitionCollection(
        mode_amount=2, target_mode_index=1, transmission_data=sample_transmission_data
    )
    df = model.target_output_dataframe
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 4)  # One row where target_mode_output == 1
    assert df.iloc[0]["target_mode_output"] == 1


# Test cases for edge cases and error handling
def test_optical_state_transitions_empty_data():
    model = OpticalStateTransitionCollection(
        mode_amount=2, target_mode_index=1, transmission_data=[]
    )
    df = model.dataframe
    assert isinstance(df, pd.DataFrame)
    assert df.empty


# TODO fix this
# def test_optical_state_transitions_missing_keys():
#     incomplete_data = [
#         {
#             "phase": (0.5, 1.0),
#             "input_fock_state": (1, 0)
#             # Missing output_fock_state and target_mode_output
#         }
#     ]
#     model = OpticalStateTransitionCollection(
#         mode_amount=2,
#         target_mode_index=1,
#         transmission_data=incomplete_data
#     )
#     df = model.transition_dataframe
#     # Ensure it handles missing keys by excluding them from the DataFrame
#     assert 'output_fock_state' not in df.columns
#     assert 'target_mode_output' not in df.columns


def test_optical_state_transitions_invalid_phase_transition_type():
    invalid_data = [
        {
            "phase": "invalid_phase",  # Invalid phase type
            "input_fock_state": (1, 0),
            "output_fock_state": (0, 1),
            "target_mode_output": 1,
        }
    ]
    with pytest.raises(ValueError):
        OpticalStateTransitionCollection(
            mode_amount=2, target_mode_index=1, transmission_data=invalid_data
        )


# TODO fix this
# def test_optical_state_transitions_invalid_mode_amount():
#     with pytest.raises(ValueError):
#         OpticalStateTransitionCollection(
#             mode_amount=-1,  # Invalid mode amount
#             target_mode_index=1,
#             transmission_data=sample_transmission_data
#         )
