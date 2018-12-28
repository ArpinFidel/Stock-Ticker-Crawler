from lib.stock_company_data_crawler import *
from lib import silence

import pandas_datareader.data as pdr
import datetime
import os

companies = []
blacklistedCompanies = []
tickers = {}
tickerSources = ['google', 'iex', 'fred', 'morningstar', 'quandl', 'robinhood']

def get_new_company_data():
	global companies
	runPath = os.path.dirname(os.path.abspath(__file__))
	browserPath = runPath+'\\lib\\chromedriver.exe'

	with silence.no_stdout():
		companies = get_company_data(browserPath)
	
	companyFile = open('.\\lib\\companies.txt', 'w+')
	for c in companies:
		companyFile.write('%s^%s^%s^%s^%s\n' % (c.code, c.name, c.recDate, c.stock, c.board))


def read_company_data():
	global companies
	companyFile = open('.\\lib\\companies.txt', 'r')
	companies=[Company(c.split('^')) for c in companyFile.read().splitlines()]
	companyFile.close()

if __name__ == '__main__':
	
	print('Loading company list...')
	
	read_company_data()
	if len(companies) == 0:
		print('Fetching company list. Please wait.')
		get_new_company_data()
	
	
	start = datetime.datetime(2013, 1, 1)
	end = datetime.datetime(2013, 1, 27)
	
	print('Fetching tickers...')
	
	for c in companies[:10]:
		print()
		success = 0
		for source in tickerSources:
			try:
				print('Fetching tickers for %s from %s' % (c.code, source))
				ticker = pdr.DataReader(c.code if source != 'quandl' else c.code+'.ID', source, start, end)
			except Exception as e:
				# print(e)
				print('Failed to get ticker for %s from %s' % (c.code, source))
				continue
				
			tickers[c.code] = ticker
			print('Succesfully fetched tickers for %s' % (c.code))
			success = 1
			break
		
		if not success: blacklistedCompanies.append(c)
	
	print('Succesfully fetched tickers for %d companies out of %d' % (len(companies)-len(blacklistedCompanies), len(blacklistedCompanies)))
	
	menu = {
		1:'Update company list',
		2:'Show company list',
		3:'Show company ticker'}
	
	while True:
		for m in menu:
			print('%d. %s' % (m, menu[m]))
		
		cMenu = input(' >> ')
		
		if cMenu == 1:
			print('Fetching company list. Please wait.')
			get_new_company_data()
		elif cMenu == 2:
			for c in companies:
				if c not in blacklistedCompanies:
					print('Symbol: %\tName: %s' % (c.code, c.name))
		elif cMenu == 3:
			cSymbol = input(' >> input company symbol: ')
			