"""Small unit inputs test software edge cases; these are not research datasets."""
import math, unittest
from types import SimpleNamespace
from stats_common import clean,number,infer,prepare
from pure_python_stats import summarize as pure
from pandas_stats import summarize as pandas
from polars_stats import summarize as polars
from compare_results import compare

class StatisticsTests(unittest.TestCase):
 def test_edge_statistics(self):
  cases=[{'x':[],'label':[]},{'x':[None],'label':[None]},
   {'x':[4.0],'label':['one']},{'x':[0.,0.,0.],'label':['b','a','b']},
   {'x':[1.,None,3.,5.],'label':['b','a',None,'a']},
   {'x':[1e12+1,1e12+2,1e12+3],'label':['b','a','b']}]
  for data in cases:
   for ddof in [0,1]:
    a,_=pure(data,{'x':'numeric','label':'categorical'},ddof)
    for fn in [pandas,polars]:
     b,_=fn(data,{'x':'numeric','label':'categorical'},ddof);compare(a,b)
  self.assertEqual(pure({'x':[1.,3.,5.]},{'x':'numeric'},1)[0]['x']['std'],2.)
 def test_input_semantics(self):
  self.assertIsNone(clean(' N/A '));self.assertEqual(clean('0'),'0')
  self.assertEqual(number('$1,234.50'),1234.5);self.assertEqual(number('(4)'),-4)
  self.assertEqual(number('50%'),.5);self.assertIsNone(number('1,2'));self.assertIsNone(number('1e999'))
  self.assertEqual(infer('account_id',['001','002']),'identifier')
  self.assertEqual(infer('amount',['1','oops','3']),'categorical')
  self.assertEqual(infer('amount',[None,None]),'empty')
  self.assertEqual(infer('day',['2024-01-01','2024-02-29']),'datetime')
  self.assertEqual(infer('day',['2024-02-30']),'categorical')
if __name__=='__main__':unittest.main()
