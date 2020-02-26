import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_pdf import PdfPages

def ImportToDf(path, delimiter = None, header = 0, names = []):
	if names:
		return pd.read_csv(path, delimiter = delimiter, header = header, names = names)
	return pd.read_csv(path, delimiter = delimiter, header = header)

def FilterMonth(df, year, month):
    next_month = '0'+str(int(month)+1)
    return df[(df.TIMESTAMP >= year+'-'+month)&(df.TIMESTAMP<=year+'-'+next_month)]

def ReduceTimeInterval(df, start, end):
	return df[(df.TIMESTAMP >= start) & (df.TIMESTAMP <= end)].reset_index(drop=True)

# read data
title = ImportToDf('data/soc-redditHyperlinks-title.tsv', delimiter = '\t')
body = ImportToDf('data/soc-redditHyperlinks-body.tsv', delimiter = '\t')
hyperlinks = pd.concat([title, body])

# split data into months
monthly_links = {}
for year in ['2014', '2015', '2016']:
	for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
		monthly_links[year + '-' + month] = ReduceTimeInterval(hyperlinks, year + '-' + month + '-01', year + '-' + month + '-32')
for month in ['01', '02', '03', '04']:	# months in 2017 that we have data for
	monthly_links[year + '-' + month] = ReduceTimeInterval(hyperlinks, '2017-' + month + '-01', '2017-' + month + '-32')

# calculate statistics for each month
count_all_edges = []
count_neg_edges = []
perc_neg_edges = []
month_names = []
for name, month in monthly_links.items():
	month_names.append(name)

	neg_mask = month['LINK_SENTIMENT'] == -1
	neg = month[neg_mask]
	count_neg = neg['LINK_SENTIMENT'].count()
	count_neg_edges.append(count_neg)

	count_all = month['LINK_SENTIMENT'].count()
	count_all_edges.append(count_all)

	perc_neg_edges.append(count_neg / count_all)

pdf = PdfPages("Negative Edges Monthly.pdf")

plt.title("Number of edges over months")
plt.plot(month_names, count_neg_edges, color="b", label='Negative edges')
plt.plot(month_names, count_all_edges, color="r", label='All edges')
plt.legend()
plt.xticks(rotation=90)
pdf.savefig()
plt.show()

plt.title("Percentage of negative edges over months")
plt.plot(month_names, perc_neg_edges)
plt.xticks(rotation=90)
pdf.savefig()
plt.show()

pdf.close()
