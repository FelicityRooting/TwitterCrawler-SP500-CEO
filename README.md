# TwitterCrawler
What were these bosses thinking everyday ...?


# 3rd party package/dependencies

- pandas    https://pandas.pydata.org/pandas-docs/stable/index.html
- tweepy    https://github.com/tweepy/tweepy
- SECEdgar  https://github.com/GalaxyXC/sec-edgar
- TextBlob  http://textblob.readthedocs.io/en/dev/advanced_usage.html#sentiment-analyzers
- nltk      http://www.nltk.org/
- sklearn   http://scikit-learn.org/stable/modules/neural_networks_supervised.html


* SEC-Edgar's code is MODIFIED to enhance functionality.
* <Crawler.py>
  -   print x -> print(x)         # Py2 to Py3 environments.
  -   except e: -> except as e:   # Py2 to Py3 environments.
  -   In "base_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=... "
  -   &datea: retrieve report After date str(priorto) -> &dateb: retrieve report Before date str(priorto)
  -   soup = BeautifulSoup(data) -> soup = BeautifulSoup(data, "lxml") #suppress parser warning
  -   ......
