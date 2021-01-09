# Pyfunds

## Project description

Python module to get several financial information from:
* Funds data from Morningstar.
* FOREX forecast from fxstreet.


## Install
Install from PyPI with pip
```
$ pip install pyfunds
```

From development:
``` 
$ git clone git://github.com/calabozo/pyfunds.git
$ cd pyfunds/src
$ python setup.py install
```

## Usage examples

### MorningStar

Downloads fund information as Pandas dataframe:
```
>>> from pyfunds import MorningStar
>>> isins = ["IE00B4K9F548", "LU0389812933", "LU0996180864"]
>>> m = MorningStar(ISINs=isins, currency='EUR')
>>> m.df_values.head()
            IE00B4K9F548  LU0389812933  LU0996180864
date                                                
2012-03-29        100.00        118.89        117.23
2012-03-30        101.01        118.92        116.91
2012-03-31        101.01        118.92        116.91
2012-04-01        101.01        118.92        116.91
2012-04-02        102.57        118.93        116.31
```

Calculates ROI and variance on the desired window size:

```
>>> roi,var=m.calc_roi_var(num_days=365)
>>> roi.tail()
            IE00B4K9F548  LU0389812933  LU0996180864
date                                                
2021-01-03      0.963690      1.039080      1.035677
2021-01-04      0.970858      1.039891      1.047978
2021-01-05      0.967103      1.039951      1.031032
2021-01-06      0.979108      1.037582      1.037382
2021-01-07      0.981496      1.036524      1.042085
>>> var.tail()
            IE00B4K9F548  LU0389812933  LU0996180864
date                                                
2021-01-03      0.011677      0.000315      0.004829
2021-01-04      0.011468      0.000315      0.004720
2021-01-05      0.011261      0.000315      0.004654
2021-01-06      0.011064      0.000315      0.004575
2021-01-07      0.010872      0.000316      0.004518

```

