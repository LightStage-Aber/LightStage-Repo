import pandas as pd
import scipy.stats as ss

def print_column_names( df ):
	print( df.columns.values.tolist() )
	# or list(df), but this is slower.

def print_row( df, i ):
	print( df.iloc[i] )

def filter_by_column( df, col, vals=[] ):
	return df[df[ col ].isin( vals )]

filename = "lambertian_led_sets_single-loaded-result-file-reevaluation.csv"
df = pd.read_csv(filename, names=range(4005))
#row1 = df.iloc[0]
#l = eval(row1[12])

#print_column_names( df )
#print_row( df, 0 )
new_df = filter_by_column( df, col=10, vals=['../results/Control_91-92_March2017/l91.csv'] )
first_match = new_df.iloc[0]
l = first_match[12]
l = eval(l)

assert type(l) == list and len(l) == 180 and all( [(type(x) == float) for x in l]), "Validate surface intensity values."

print ss.stats.pearsonr(l, range(len(l)))
print ss.stats.pearsonr(l, range(len(l),0,-1))

print ss.stats.spearmanr(l, range(len(l)))
print ss.stats.spearmanr(l, range(len(l),0,-1))
