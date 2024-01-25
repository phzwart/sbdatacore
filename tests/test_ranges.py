from sbdatacore.ranges import *

import pytest


def test_file_names():
  base="lysozyme_1_####.img"
  obj = SerialFileNameHandler(base)
  assert obj.base=="lysozyme_1_"
  assert obj.extension == ".img"
  assert obj.n == 4
  assert obj.name_from_number( 23 ) == "lysozyme_1_0023.img"

  base="lysozyme_1.####"
  obj = SerialFileNameHandler(base)
  assert obj.base=="lysozyme_1."
  assert obj.extension == ""
  assert obj.n == 4
  assert obj.name_from_number( 23 ) == "lysozyme_1.0023"

  base = "######.lysozyme_1.img"
  obj = SerialFileNameHandler(base)
  assert obj.base==""
  assert obj.extension == ".lysozyme_1.img"
  assert obj.n == 6
  assert obj.name_from_number( 23 ) == "000023.lysozyme_1.img"
  lst = obj.names_from_range_list( [1,2,3] )
  assert lst[0] == "000001.lysozyme_1.img"
  assert lst[1] == "000002.lysozyme_1.img"
  assert lst[2] == "000003.lysozyme_1.img"
  assert len(lst)==3


  base = "######.lysozyme_1.img"
  obj = SerialFileNameHandler(base)
  range_txt = "1-3"
  name_list =  obj.names_from_range(range_txt)
  assert name_list[0] == '000001.lysozyme_1.img'
  assert name_list[1] == '000002.lysozyme_1.img'
  assert name_list[2] == '000003.lysozyme_1.img'

def test_ranges():
  range_txt="1-9,10,11,13-16"
  result = range_to_list( range_parser( range_txt ) )
  tst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]
  for ii, jj in zip(result,tst):
    assert(ii==jj)
  range_txt="1-9 10 11 13-16"
  result = range_to_list( range_parser( range_txt ) )
  tst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16]
  for ii, jj in zip(result,tst):
    assert(ii==jj)


def test_parse_file_names():
    test_cases = [
        (["file1.txt", "file2.txt", "file3.txt", "file5.txt", "file16.txt", "file300.txt", "file310.txt"],
         ("file#.txt", "1-3,5,16,300,310")),
        (["image_001.png", "image_002.png", "image_003.png", "image_100.png", "image_102.png"],
         ("image_###.png", "1-3,100,102")),
        (["doc_part1.docx", "doc_part2.docx", "doc_part3.docx"],
         ("doc_part#.docx", "1-3"))
    ]

    for files, expected in test_cases:
        basename, range_str = parse_file_names(files)
        assert (basename, range_str) == expected, f"Failed for {files}. Expected {expected}, got {(basename, range_str)}"


def test_mixit():
    test_cases = [
        (["file1.txt", "file2.txt", "file3.txt", "file5.txt", "file16.txt", "file300.txt", "file310.txt",
          "image_001.png", "image_002.png", "image_003.png", "image_100.png", "image_102.png",
          "doc_part1.docx", "doc_part2.docx", "doc_part3.docx","my_last_bank.statement"],


         [("file#.txt", "1-3,5,16,300,310"),
          ("image_###.png", "1-3,100,102"),
          ("doc_part#.docx", "1-3") ])
    ]
    for fl in test_cases:
        fs, orphan = parse_file_list(fl[0])
        for item in fs:
            assert (str(item)) in str(fl[1])
