import unittest
from unittest.mock import patch, mock_open
import logging
import mcnp_output_reader
import neut_utilities as ut
import os


class version_test_case(unittest.TestCase):
    """ test for reading the version of output file"""

    def test_is_version(self):
        """ test when a version is in the list of strings """
        list_a = ["          Code Name & Version = MCNP6, 1.0",
                  "  "]
        self.assertEqual(mcnp_output_reader.read_version(list_a), "MCNP6, 1.0")

    def test_is_version_none_given_other_list(self):
        """ test for only allocating if an actual  version not a random string"""
        list_a = ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                  "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                  "ccccccccccccccccccccccccccccccccccccccccccccccccc",
                  "ddddddddddddddddddddddddddddddddddddddddddddddddd"]
        list_b = ["a", "b", "c", "d"]
        self.assertIsNone(mcnp_output_reader.read_version(list_a))
        self.assertIsNone(mcnp_output_reader.read_version(list_b))

    def test_is_version_none_given_string(self):
        """ test for version with string"""
        string_a = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        self.assertIsNone(mcnp_output_reader.read_version(string_a))

    def test_empty_input(self):
        """ test for empty list given """
        empty_list = []
        self.assertIsNone(mcnp_output_reader.read_version(empty_list))


class read_warnings_test_case(unittest.TestCase):

    def test_read_comments_warnings_successful(self):
        """ Test when comments and warnings are present in the lines """
        lines = [
            "  comment. This is a comment.",
            "  warning. This is a warning.",
            "Some other line"
        ]
        result_comments, result_warnings = mcnp_output_reader.read_comments_warnings(lines)

        self.assertEqual(result_comments, ["  comment. This is a comment."])
        self.assertEqual(result_warnings, ["  warning. This is a warning."])

    def test_read_comments_warnings_no_comments_warnings(self):
        """ Test when there are no comments or warnings in the lines """
        lines = ["Some other line"]
        result_comments, result_warnings = mcnp_output_reader.read_comments_warnings(lines)

        self.assertEqual(result_comments, [])
        self.assertEqual(result_warnings, [])

    def test_read_multiple_comments_warnings_successful(self):
        """ Test when multiple comments and warnings are present in the lines """
        lines = [
            "  comment. This is a comment.",
            "  warning. This is a warning.",
            "Some other line",
            "  comment. This is a comment.",
            "  warning. This is a warning.",
        ]
        result_comments, result_warnings = mcnp_output_reader.read_comments_warnings(lines)

        self.assertEqual(len(result_comments), 2)
        self.assertEqual(len(result_warnings), 2)


class get_tally_nums_test_case(unittest.TestCase):
    """ test for get talyl num """

    def test_get_tally_num(self):
        # test with a set of differnt tally types
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        data = ut.get_lines(path)
        tnums = mcnp_output_reader.get_tally_nums(data)
        self.assertEqual(len(tnums), 6)
        self.assertIn("1", tnums)
        self.assertIn("2", tnums)
        self.assertIn("4", tnums)
        self.assertIn("5", tnums)
        self.assertIn("6", tnums)
        self.assertIn("8", tnums)

    def test_tally_count(self):
        # test assignment of mcnp output object num_tallies
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        single = mcnp_output_reader.read_output_file(path)
        self.assertEqual(single.num_tallies, 6)


class rendevous_test_case(unittest.TestCase):
    """ test for reading the version of output file"""

    def test_count_rendevous_tests(self):

        # test with a single core job count should be 0
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        data = ut.get_lines(path)
        count = mcnp_output_reader.count_rendevous(data)
        self.assertEqual(count, 0)

        # need to add test for multicore job

    def test_index_rendevous_tests(self):

        # test with a single core job should be 0
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        data = ut.get_lines(path)
        index = mcnp_output_reader.get_rendevous_index(data)
        self.assertEqual(index, [])

        # need to add test for multicore job


class stat_test_case(unittest.TestCase):
    """ test for reading the version of output file"""

    def test_read_stat_tests(self):
        self.assertTrue(True)
        # need to add test for tally with all 0.0 bins


class tally_type1_tests(unittest.TestCase):
    """ tests for type 1 tally """

    def test_single_value_t1_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 1:
                self.assertEqual(tn.tally_type, '1')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertEqual(tn.eng, None)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(tn.ang_bins, None)
                self.assertEqual(len(tn.result), 1)
                self.assertEqual(len(tn.err), 1)
                self.assertEqual(tn.result[0], 1.16486E+00)
                self.assertEqual(tn.err[0], 0.0006)

    def test_ebined_t1_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_erg.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 1:
                self.assertEqual(tn.tally_type, '1')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertNotEqual(tn.eng, None)
                self.assertEqual(len(tn.eng), 14)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(tn.ang_bins, None)
                self.assertEqual(len(tn.result), 14)
                self.assertEqual(len(tn.err), 14)
                self.assertEqual(tn.result[0], 2.92000E-02)

    def test_tbinned_t1_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_t.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 1:
                self.assertEqual(tn.tally_type, '1')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 200000)
                self.assertEqual(tn.eng, None)
                self.assertNotEqual(tn.times, None)
                self.assertEqual(len(tn.times), 14)
                self.assertEqual(tn.times[-1], "total")
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result), 14)
                self.assertEqual(len(tn.err), 14)
                self.assertEqual(tn.result[-1], 2.44655e-1)
                self.assertEqual(tn.err[-1], 0.0039)


class tally_type2_tests(unittest.TestCase):
    """ tests for type 2 tally """

    def test_single_value_t2_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 2:
                self.assertEqual(tn.tally_type, '2')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertEqual(tn.eng, None)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(tn.ang_bins, None)
                self.assertEqual(len(tn.result), 1)
                self.assertEqual(len(tn.err), 1)
                self.assertEqual(tn.result[0], 4.31795E-03)
                self.assertEqual(tn.err[0], 0.0015)

    def test_ebined_t2_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_erg.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 2:
                self.assertEqual(tn.tally_type, '2')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertNotEqual(tn.eng, None)
                self.assertEqual(len(tn.eng), 14)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(tn.ang_bins, None)
                self.assertEqual(len(tn.result), 14)
                self.assertEqual(len(tn.err), 14)
                self.assertEqual(tn.result[0], 1.92767E-04)

    def test_etbinned_t2_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_et.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 2:
                self.assertEqual(tn.tally_type, '2')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertNotEqual(tn.eng, None)
                self.assertEqual(len(tn.eng), 15)
                self.assertEqual(tn.eng[-1], "total")
                self.assertNotEqual(tn.times, None)
                self.assertEqual(len(tn.times), 15)
                self.assertEqual(tn.times[-1], "total")
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(tn.ang_bins, None)
                self.assertEqual(tn.result.shape, tn.err.shape)
                self.assertEqual(tn.result.shape, (15, 15))

    def test_tbinned_t2_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_t.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 2:
                self.assertEqual(tn.tally_type, '2')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 200000)
                self.assertEqual(tn.eng, None)
                self.assertNotEqual(tn.times, None)
                self.assertEqual(len(tn.times), 14)
                self.assertEqual(tn.times[-1], "total")
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result), 14)
                self.assertEqual(len(tn.err), 14)
                self.assertEqual(tn.result[-1], 2.69842E-04)
                self.assertEqual(tn.err[-1], 0.0054)


class tally_type4_tests(unittest.TestCase):
    """ tests for type 4 tally """

    def test_single_value_t4_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 4:
                self.assertEqual(tn.tally_type, '4')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertEqual(tn.eng, None)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.err), 1)
                self.assertEqual(len(tn.result), 1)
                self.assertEqual(tn.result[0], 1.91076E-03)
                self.assertEqual(tn.err[0], 0.0006)
                self.assertEqual(tn.cells, ['2'])
                self.assertEqual(tn.vols, ['3.66519E+03'])

    def test_ebined_t4_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_erg.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 4:
                self.assertEqual(tn.tally_type, '4')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertNotEqual(tn.eng, None)
                self.assertEqual(len(tn.eng), 14)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result[0]), 14)
                self.assertEqual(len(tn.err[0]), 14)
                self.assertEqual(tn.result[0][0], 1.20226E-04)
                self.assertEqual(tn.cells, ['2'])
                self.assertEqual(tn.vols, ['3.66519E+03'])

    def test_etbinned_t4_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_et.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 4:
                self.assertEqual(tn.tally_type, '4')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertNotEqual(tn.eng, None)
                self.assertEqual(len(tn.eng), 15)
                self.assertEqual(tn.eng[-1], "total")
                self.assertNotEqual(tn.times, None)
                self.assertEqual(len(tn.times), 15)
                self.assertEqual(tn.times[-1], "total")
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(tn.result.shape, tn.err.shape)
                self.assertEqual(tn.result.shape, (15, 15))

    def test_tbinned_t4_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_t.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 4:
                self.assertEqual(tn.tally_type, '4')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 200000)
                self.assertEqual(tn.eng, None)
                self.assertNotEqual(tn.times, None)
                self.assertEqual(len(tn.times), 14)
                self.assertEqual(tn.times[-1], "total")
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result), 14)
                self.assertEqual(len(tn.err), 14)
                self.assertEqual(tn.result[-1], 1.70644e-03)
                self.assertEqual(tn.err[-1], 0.0008)


class tally_type5_tests(unittest.TestCase):
    """ tests for type 5 tally """

    def test_single_value_t5_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 5:
                self.assertEqual(tn.tally_type, '5')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertEqual(tn.eng, None)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result), 1)
                self.assertEqual(len(tn.err), 1)
                self.assertEqual(tn.result[0], 3.42950E-04)
                self.assertEqual(tn.err[0], 0.0025)
                self.assertEqual(tn.x, 15)
                self.assertEqual(tn.x, 15.0)
                self.assertEqual(tn.y, 0.00)
                self.assertEqual(tn.z, 0.00)
                self.assertEqual(tn.largest_score, 2.32897E-01)
                self.assertEqual(tn.largest_score_nps, 492485)
                self.assertEqual(tn.average_per_history, 3.42950E-04)
                self.assertEqual(tn.misses["russian roulette on pd"], 0)
                self.assertEqual(tn.misses["psc=0"], 0)
                tstring = "russian roulette in transmission"
                self.assertEqual(tn.misses[tstring], 935317)
                self.assertEqual(tn.misses["underflow in transmission"], 39376)
                self.assertEqual(tn.misses["hit a zero-importance cell"], 0)
                self.assertEqual(tn.misses["energy cutoff"], 0)

    def test_ebined_t5_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_erg.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 5:
                self.assertEqual(tn.tally_type, '5')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertNotEqual(tn.eng, None)
                self.assertEqual(len(tn.eng), 14)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result), 14)
                self.assertEqual(len(tn.err), 14)
                self.assertEqual(tn.result[0], 1.20831E-05)
                self.assertEqual(tn.x, 15)
                self.assertEqual(tn.y, 0.00)
                self.assertEqual(tn.z, 0.00)
                self.assertEqual(tn.largest_score, 2.32897E-01)
                self.assertEqual(tn.largest_score_nps, 492485)
                self.assertEqual(tn.average_per_history, 3.42950E-04)
                self.assertEqual(tn.misses["russian roulette on pd"], 0)
                self.assertEqual(tn.misses["psc=0"], 0)
                tstring = "russian roulette in transmission"
                self.assertEqual(tn.misses[tstring], 935317)
                self.assertEqual(tn.misses["underflow in transmission"], 39376)
                self.assertEqual(tn.misses["hit a zero-importance cell"], 0)
                self.assertEqual(tn.misses["energy cutoff"], 0)


class tally_type6_tests(unittest.TestCase):
    """ tests for type 6 tally """

    def test_single_value_t6_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 6:
                self.assertEqual(tn.tally_type, '6')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertEqual(tn.eng, None)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result), 1)
                self.assertEqual(len(tn.err), 1)
                self.assertEqual(tn.result[0], 4.30567E-05)
                self.assertEqual(tn.err[0], 0.0002)
                self.assertEqual(tn.cells, ['2'])
                self.assertEqual(tn.vols, ['9.89602E+03'])

    def test_ebined_t6_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_erg.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 6:
                self.assertEqual(tn.tally_type, '6')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertNotEqual(tn.eng, None)
                self.assertEqual(len(tn.eng), 14)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result[0]), 14)
                self.assertEqual(len(tn.err[0]), 14)
                self.assertEqual(tn.result[0][0], 5.60997E-07)
                self.assertEqual(tn.cells, ['2'])
                self.assertEqual(tn.vols, ['9.89602E+03'])


class tally_type8_tests(unittest.TestCase):
    """ tests for type 8 tally """

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_erg.io')
        self.single = mcnp_output_reader.read_output_file(path)

    def test_single_value_t8_tally(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles.io')
        single = mcnp_output_reader.read_output_file(path)
        for tn in single.tally_data:
            if tn.number == 8:
                self.assertEqual(tn.tally_type, '8')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertEqual(tn.eng, None)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result), 1)
                self.assertEqual(len(tn.err), 1)
                self.assertEqual(tn.result[0], 1.00000E+00)
                self.assertEqual(tn.err[0], 0.00)

    def test_ebined_t8_tally(self):
        for tn in self.single.tally_data:
            if tn.number == 8:
                self.assertEqual(tn.tally_type, '8')
                self.assertEqual(tn.particle, "photons")
                self.assertEqual(tn.nps, 1000000)
                self.assertNotEqual(tn.eng, None)
                self.assertEqual(len(tn.eng), 14)
                self.assertEqual(tn.times, None)
                self.assertEqual(tn.user_bins, None)
                self.assertEqual(len(tn.result), 14)
                self.assertEqual(len(tn.err), 14)
                self.assertEqual(tn.result[0], 5.16461E-01)


class writelines_test_case(unittest.TestCase):
    """ tests write_lines function"""

    def test_write_lines(self):
        open_mock = mock_open()
        logger = logging.getLogger()
        logger.level = logging.DEBUG
        with patch("neut_utilities.open", open_mock, create=True):
            mcnp_output_reader.print_tally_lines_to_file(["hello", "world"],
                                                         "output", 1)

        open_mock.assert_called_with("output1.txt", "w")
        open_mock.return_value.write.assert_any_call("hello\n")


class tables_testing(unittest.TestCase):
    """ test for output tables """

    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), 'test_output', 'singles_erg.io')
        self.single = mcnp_output_reader.read_output_file(path)
        self.t60 = self.single.t60

    def test_table_numbers(self):
        # tests getting all the  print table numbers
        self.assertEqual(len(self.single.tables), 4)
        self.assertEqual(self.single.tables['60'], 69)

    def test_t60(self):
        # tests print table 60 - cell information
        self.assertEqual(len(self.t60["mass"]), 4)
        self.assertEqual(len(self.t60.columns), 8)
        self.assertFalse(self.t60.empty)

    def test_t101(self):
        # tests print table 101 - particles and energy limits
        self.assertEqual(len(self.single.t101['particle_name']), 2)
        self.assertFalse(self.single.t101.empty)

    def test_t126(self):
        # test print table 126 - activity in cells
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
