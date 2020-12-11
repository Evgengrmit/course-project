# Copyright 2020 Evgenij Grigorev evgengrmit@icloud.com

import unittest
import sys, os

from collections import Counter
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../course-project"))

from detector.Preprocess import Preprocess


class MyTestCase(unittest.TestCase):
    def test_preprocess_set(self):
        prp = Preprocess()
        df = prp.set_dataset('../datasets/Dataset.csv')
        self.assertEqual(df.shape, (220000, 19))
        df = prp.set_dataset('../datasets/Test.csv')
        self.assertEqual(df.shape, (400000, 19))

    def test_preprocess_gradient(self):
        prp = Preprocess()
        prp.set_dataset('../datasets/Dataset.csv')
        train, labels = prp.process_data_for_gradient_with_label()
        self.assertEqual(labels.size, 220000)
        self.assertEqual(train.shape, (220000, 18))

    def test_preprocess_neural(self):
        prp = Preprocess()
        prp.set_dataset('../datasets/Test.csv')
        train, labels = prp.process_data_for_neural_with_label()
        self.assertEqual(labels.size, 398457)

    def test_get_balanced(self):
        prp = Preprocess()
        prp.get_balanced_dataset('../datasets/Dataset.csv',100)
        self.assertEqual(len(prp.data),100)
        self.assertEqual(Counter(prp.data['Label']),Counter({0: 50, 1: 50}))

    def test_get_imbalanced(self):
        prp = Preprocess()
        prp.get_imbalanced_dataset('../datasets/Dataset.csv',0.3,0.7, 1000)
        self.assertEqual(len(prp.data), 1000)
        self.assertEqual(Counter(prp.data['Label']), Counter({0: 700, 1: 300}))


if __name__ == '__main__':
    unittest.main()
