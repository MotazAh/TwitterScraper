from multiprocessing import Manager
from scraper import scrape_accounts

def main(verbose=2):
    urls_to_scrape = []
    
    # Get urls to scrape from file
    with open('accounts_to_scrape.txt') as f:
        urls_to_scrape = f.read().splitlines()
    
    manager = Manager()
    return_list = manager.list() # Using list to avoid locking
    
    # Get user inputs
    symbol = input('Enter cash tag (without $ sign): ')
    symbol = '\\$' + symbol
    time_interval = int(input('Enter time interval (minutes): '))
    
    # Start the scraping process
    scrape_accounts(return_list, symbol, urls_to_scrape, time_interval, verbose)

if __name__ == '__main__':
    main(1)