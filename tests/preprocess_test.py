import unittest
import sys

sys.path.append("../..")

from source.Preprocess import Preprocess


class MyTestCase(unittest.TestCase):
    def test_preprocess_set(self):
        prp = Preprocess()
        df = prp.set_dataset('datasets/Dataset.csv')
        self.assertEqual(df.shape, (220000, 19))
        df = prp.set_dataset('datasets/Test.csv')
        self.assertEqual(df.shape, (400000, 19))

    def test_preprocess_gradient(self):
        prp = Preprocess()
        prp.set_dataset('datasets/Dataset.csv')
        train, labels = prp.process_data_for_gradient()
        self.assertEqual(labels.size, 220000)
        self.assertEqual(train.shape, (220000, 18))

    def test_preprocess_neural(self):
        prp = Preprocess()
        prp.set_dataset('datasets/Test.csv')
        train, labels = prp.process_data_for_neural()
        self.assertEqual(labels.size, 398457)

if __name__ == '__main__':
    unittest.main()
