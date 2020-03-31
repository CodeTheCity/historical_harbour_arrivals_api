#!/usr/bin/env python3

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mpl_dates
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import io
from flask import Flask, render_template, send_file, make_response, request
import datetime
import database_driver
import pandas as pd
import configparser, os
import numpy as np

app = Flask(__name__)
dbname = 'harbour.db'
db = database_driver.database(dbname)

def getCargoData():
	rows = db.select('SELECT DISTINCT cargo FROM arrivals ORDER BY cargo')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getVesselsData():
	rows = db.select('SELECT DISTINCT vessel FROM arrivals ORDER BY vessel')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getRegisteredPortsData():
	rows = db.select('SELECT DISTINCT registered_port FROM arrivals ORDER BY registered_port')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getFromPortsData():
	rows = db.select('SELECT DISTINCT from_port FROM arrivals ORDER BY from_port')
	data = []
	for row in rows:
		data.append(row[0])

	return data

@app.route('/')
# main route
def index():

	cargo = []
	vessels = []
	registered_ports = []
	from_ports = []
	try:
		cargo = getCargoData()
	except Exception as e:
		print(e)

	try:
		vessels = getVesselsData()
	except Exception as e:
		print(e)

	try:
		registered_ports = getRegisteredPortsData()
	except Exception as e:
		print(e)

	try:
		from_ports = getFromPortsData()
	except Exception as e:
		print(e)

	templateData = {
		'cargo' : cargo,
		'vessels' : vessels,
		'registered_ports' : registered_ports,
		'from_ports' : from_ports
	}
	return render_template('index.html', **templateData)

def buildCargoGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, cargo FROM arrivals WHERE strftime(\'%Y\', date) = "{}" ORDER BY date'.format(year), con, parse_dates=['date'], index_col=['date'])
	con.close()

	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)

	if df.empty == False:
		df_cargos = df.groupby('date').cargo.value_counts().unstack().fillna(0)

	

		columns = df_cargos.columns
		labels = columns.values.tolist()

		colour_map = cm.get_cmap('tab20', len(columns) + 1)

		x = df_cargos.index
		bottom = np.zeros(df_cargos.shape[0])
		for i, column in enumerate(columns, start=0):
			axis.bar(x, df_cargos[column].values.tolist(), bottom=bottom, label=column, color=colour_map.colors[i])
			bottom += df_cargos[column].values.tolist()

	date_format = mpl_dates.DateFormatter('%d %b %Y')
	axis.xaxis_date()
	axis.xaxis.set_major_formatter(date_format)
	axis.set_title('Cargo arrival at Aberdeen {}'.format(year))
	axis.legend(fontsize=10, ncol=4)

	fig.autofmt_xdate()
	fig.tight_layout()

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/cargo/1914')
def plot_cargo1914():
	return buildCargoGraph(1914)
	
@app.route('/plot/cargo/1915')
def plot_cargo1915():
	return buildCargoGraph(1915)

@app.route('/plot/cargo/1916')
def plot_cargo1916():
	return buildCargoGraph(1916)

@app.route('/plot/cargo/1917')
def plot_cargo1917():
	return buildCargoGraph(1917)

@app.route('/plot/cargo/1918')
def plot_cargo1918():
	return buildCargoGraph(1918)

@app.route('/plot/cargo/1919')
def plot_cargo1919():
	return buildCargoGraph(1919)

@app.route('/plot/cargo/1920')
def plot_cargo1920():
	return buildCargoGraph(1920)

if __name__ == '__main__':
	config = configparser.ConfigParser()

	if not os.path.exists('config.ini'):
		config['server'] = {'port': '80'}
		config.write(open('config.ini', 'w'))
	config.read('config.ini')
	app.run(debug=False, port=config['server']['port'], host='0.0.0.0')