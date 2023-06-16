# Project Structure Usage

It is very simple and follows convention. You need to structure your logic design files in a directory with this structure:

Pre-generation file required configuration
```
    design_folder_name
        io/
            pin_order.cfg # Required: OpenRoad
        model/
            design_model.py # Optional: cocotb
        sdc/
            design.sdc # Required: OpenRoad
        src/
            source_files.v # Required by all
        tb/
            test_design.py # Required cocotb
```

If you run the full flow, the design folder should look like:

```
    design_folder_name
        io/
            pin_order.cfg # Required: OpenRoad
        model/
            design_model.py # Optional: cocotb
        runs/
            openlane_run_folder # Required OpenRoad
        sdc/
            design.sdc # Required: OpenRoad
        src/
            source_files.v # Required by all
        tb/
            test_design.py # Required cocotb
```
