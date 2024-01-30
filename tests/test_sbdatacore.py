#!/usr/bin/env python

"""Tests for `sbdatacore` package."""

import pytest
from tests import generate_test_data
import os
import shutil
from sbdatacore import parse_ALS_data
from sbdatacore import make_summary


def test_all():
    # make data and go to incoming subdir
    generate_test_data.run()
    current_directory = os.getcwd()
    new_directory = os.path.join(current_directory, "sbdatacore_test")
    os.chdir(new_directory)
    # now run the processor
    assert parse_ALS_data.process_ALS_data(new_directory,
                                           os.path.join(new_directory,"data.base")
                                           )
    result = make_summary.list_dirs_with_file_count(new_directory)
    result = result.replace(" ", "").replace("\n","")
    expected_result = "├──/(1files)│data.base├──incoming/└──data/└──users/├──mpence/│└──ALS/│├──2024_01_01/││└──mother/││└──Pin1/││└──screen/(6files)││('Pin1_0_#####.jpg','1-2')││('Pin1_0_#####.cbf','1-2')││('Pin1_0_#####.txt','1-2')│└──2024_02_12/│└──mother/│├──Pin3/││├──screen/(6files)│││('Pin3_0_#####.cbf','1-2')│││('Pin3_0_#####.jpg','1-2')│││('Pin3_0_#####.txt','1-2')││├──collect/(12files)│││('Pin3_1_#####.cbf','1-12')││└──processed/││├──DIALS/│││└──DIALS_Pin3_1/(1files)│││results.txt││└──XDS/││└──XDS_Pin3_1/(1files)││results.txt│└──Pin2/│├──screen/(6files)││('Pin2_0_#####.jpg','1-2')││('Pin2_0_#####.cbf','1-2')││('Pin2_0_#####.txt','1-2')│├──collect/(12files)││('Pin2_1_#####.cbf','1-12')│└──processed/│├──DIALS/││└──DIALS_Pin2_1/(1files)││results.txt│└──XDS/│└──XDS_Pin2_1/(1files)│results.txt└──kharris/└──ALS/├──2023_01_23/│└──snoopy/│└──Pin1/│├──screen/(6files)││('Pin1_0_#####.jpg','1-2')││('Pin1_0_#####.cbf','1-2')││('Pin1_0_#####.txt','1-2')│├──collect/(12files)││('Pin1_1_#####.cbf','1-12')│└──processed/│├──DIALS/││└──DIALS_Pin1_1/(1files)││results.txt│└──XDS/│└──XDS_Pin1_1/(1files)│results.txt└──2023_12_12/└──peanut/└──Pin2/├──screen/(6files)│('Pin2_0_#####.jpg','1-2')│('Pin2_0_#####.cbf','1-2')│('Pin2_0_#####.txt','1-2')├──collect/(12files)│('Pin2_1_#####.cbf','1-12')└──processed/├──DIALS/│└──DIALS_Pin2_1/(1files)│results.txt└──XDS/└──XDS_Pin2_1/(1files)results.txt"
    assert result == expected_result

    #now remove all files
    for root, dirs, files in os.walk(new_directory, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
            #print(f"Removed file: {file_path}")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            shutil.rmtree(dir_path)
            #print(f"Removed directory: {dir_path}")
    shutil.rmtree(new_directory)



