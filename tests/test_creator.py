from unittest import TestCase, main
from unittest.mock import patch, mock_open

from app import Creator, constants


class TestCreator(TestCase):
    input_file = "files/dummy_input.txt"
    output_file = "files/dummy_output.txt"

    def setUp(self):
        self.creator = Creator(self.input_file, self.output_file)

    @patch("builtins.open", new_callable=mock_open, read_data='C 20 4\nL 1 2 6 2\nL 6 3 6 4\nR 16 1 20 3\nB 10 3 o')
    def test_ok(self, mock_files):
        self.creator.execute()

        mock_files.assert_called()
        self.assertEqual(mock_files.call_count, 2)
        mock_files.assert_called_with(self.output_file, 'w')
        self.assertEqual(mock_files().write.call_count, 5)

    @patch("builtins.open", new_callable=mock_open, read_data='\n')
    def test_fail_invalid_string(self, mock_files):
        with self.assertRaises(ValueError) as context:
            self.creator.execute()

        self.assertTrue(constants.ERROR_MESSAGE_NO_FIGURE in str(context.exception))

        mock_files.assert_called()
        self.assertEqual(mock_files.call_count, 2)
        self.assertEqual(mock_files(self.output_file).write.call_count, 0)

    @patch("builtins.open", new_callable=mock_open, read_data='C 20 4\nD 1 2 6 2')
    def test_fail_invalid_shape_name(self, mock_files):
        with self.assertRaises(ValueError) as context:
            self.creator.execute()

        self.assertTrue(constants.ERROR_MESSAGE_NO_FIGURE in str(context.exception))

        mock_files.assert_called()
        self.assertEqual(mock_files.call_count, 2)
        self.assertEqual(mock_files(self.output_file).write.call_count, 1)

    @patch("builtins.open", new_callable=mock_open, read_data='C 20 4\nL 1 2')
    def test_fail_lack_of_shape_params(self, mock_files):
        with self.assertRaises(Exception) as context:
            self.creator.execute()

        self.assertTrue('Invalid Line input data - expected 4 params, but 2 were given' in str(context.exception))

        mock_files.assert_called()
        self.assertEqual(mock_files.call_count, 2)
        self.assertEqual(mock_files(self.output_file).write.call_count, 1)

    @patch("builtins.open", new_callable=mock_open, read_data='C 20 4\nL 1 2 a f')
    def test_fail_shape_wrong_params(self, mock_files):
        with self.assertRaises(Exception) as context:
            self.creator.execute()

        self.assertTrue(f'{constants.ERROR_MESSAGE_FAILED_PARAM} Line' in str(context.exception))

        mock_files.assert_called()
        self.assertEqual(mock_files.call_count, 2)
        self.assertEqual(mock_files(self.output_file).write.call_count, 1)

    @patch("builtins.open", new_callable=mock_open, read_data='C 20 4\nB 111 2 o')
    def test_fail_point_out_of_canvas(self, mock_files):
        with self.assertRaises(Exception) as context:
            self.creator.execute()

        self.assertTrue(f'Fill {constants.ERROR_MESSAGE_POINT_OUT_OF_CANVAS}' in str(context.exception))

        mock_files.assert_called()
        self.assertEqual(mock_files.call_count, 2)
        self.assertEqual(mock_files(self.output_file).write.call_count, 1)

    @patch("builtins.open", new_callable=mock_open, read_data='L 1 2 1 8\nC 20 4')
    def test_fail_no_canvas(self, mock_files):
        with self.assertRaises(Exception) as context:
            self.creator.execute()

        self.assertTrue(constants.ERROR_MESSAGE_NO_CANVAS in str(context.exception))

        mock_files.assert_called()
        self.assertEqual(mock_files.call_count, 2)
        self.assertEqual(mock_files(self.output_file).write.call_count, 0)

    @patch("builtins.open", new_callable=mock_open)
    def test_fail_no_file(self, mock_files):
        error_message = 'No such file or directory'
        mock_files.side_effect = FileNotFoundError(error_message)

        with self.assertRaises(FileNotFoundError) as context:
            self.creator.execute()

        self.assertTrue(error_message in str(context.exception))


if __name__ == '__main__':
    main()
