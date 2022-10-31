"""
Main code.
"""
import pandas as pd

import database


def create_session(db_filepath):
    """Return a handle to the database."""
    engine = database.connect(db_filepath)
    database.create_tables(engine)
    session = database.create_session(engine)

    return session


def get_indicators(company_data):
    """Return a collection with calculated financial indicators."""
    indicators = {
        'P/E':          (company_data.market_price, company_data.net_profit),
        'P/S':          (company_data.market_price, company_data.sales),
        'P/B':          (company_data.market_price, company_data.assets),
        'ND/EBITDA':    (company_data.net_debt, company_data.ebitda),
        'ROE':          (company_data.net_profit, company_data.equity),
        'ROA':          (company_data.net_profit, company_data.assets),
        'L/A':          (company_data.liabilities, company_data.assets),
    }

    for indicator, (value_1, value_2) in indicators.items():
        try:
            value = round(value_1 / value_2, 2)
        except TypeError:
            value = None
        finally:
            indicators[indicator] = value

    return indicators


class Menu:
    """Class that represents a general menu for Investor Program."""

    def __init__(self, menu=None):
        self.menu = menu

    def __repr__(self):
        pass

    def __str__(self, menu_type='MENU'):
        msg = menu_type + '\n'

        for option_id, option in self.menu.items():
            msg += f'{option_id} {option}\n'

        return msg

    def isvalid_option(self, option):
        """Check that the selected option is valid."""
        return True if option in self.menu else False


class MainMenu(Menu):
    """Class that represents the main menu."""

    MENU = {
        0: 'Exit',
        1: 'CRUD operations',
        2: 'Show top ten companies by criteria',
    }

    def __init__(self):
        super().__init__(MainMenu.MENU)

    def __str__(self):
        return super().__str__('MAIN MENU')


class CrudMenu(Menu):
    """Class that represents the CRUD menu."""

    MENU = {
        0: 'Back',
        1: 'Create a company',
        2: 'Read a company',
        3: 'Update a company',
        4: 'Delete a company',
        5: 'List all companies',
    }

    def __init__(self):
        super().__init__(CrudMenu.MENU)

    def __str__(self):
        return super().__str__('CRUD MENU')

    @staticmethod
    def get_company_input():
        """Return a dict with values to fill `company` table with user input."""
        entry = {
            'ticker': input('Enter ticker (in the format "MOON"):\n'),
            'name': input('Enter company( in the format "Moon Corp"):\n'),
            'sector': input('Enter industries( in the format "Technology"):\n')
        }

        return entry

    @staticmethod
    def get_financial_input():
        """Return a dict with values to fill 'financial' table with user input."""
        entry = {
            'ebitda': input('Enter ebitda (in the format "987654321"):\n'),
            'sales': input('Enter sales (in the format "987654321"):\n'),
            'net_profit':
                input('Enter net profit (in the format "987654321"):\n'),
            'market_price':
                input('Enter market price (in the format "987654321"):\n'),
            'net_debt': input('Enter net debt (in the format "987654321"):\n'),
            'assets': input('Enter assets (in the format "987654321"):\n'),
            'equity': input('Enter equity (in the format "987654321"):\n'),
            'cash_equivalents':
                input('Enter cash equivalents (in the format "987654321"):\n'),
            'liabilities':
                input('Enter liabilities (in the format "987654321"):\n')
        }

        return entry

    @staticmethod
    def create_company(session):
        # Ask for input and create a company in the companies table
        entry_companies = CrudMenu.get_company_input()
        database.add_entry(session, 'companies', entry_companies)

        # Ask for input and create financial data in the financial table
        entry_financial = CrudMenu.get_financial_input()
        entry_financial['ticker'] = entry_companies['ticker']
        database.add_entry(session, 'financial', entry_financial)

        session.commit()

        print('Company created successfully!')

    @staticmethod
    def read_company(session):
        # Ask for a company name
        company_name = input('Enter company name:\n')

        # Search the database for the company name
        companies = database.get_company_by_name(session, company_name)

        if len(companies):
            # List matching companies
            company_selection = {}
            for i, company in enumerate(companies):
                company_selection[i] = {
                    'ticker': company.ticker, 'name': company.name
                }
                print(f'{i} {company.name}')

            # Ask for a company number
            company_number = int(input('Enter company number:\n'))
            company = company_selection[company_number]
            print(f"{company['ticker']} {company['name']}")

            # Calculate the financial indicators
            company_data = \
                database.get_financial_by_ticker(session, company['ticker'])
            indicators = get_indicators(company_data)

            # Print the indicators
            for indicator_name, indicator_value in indicators.items():
                print(f'{indicator_name} = {indicator_value}')
        else:
            print('Company not found!')

    @staticmethod
    def update_company(session):
        # Ask for a company name
        company_name = input('Enter company name:\n')

        # Search the database for the company name
        companies = database.get_company_by_name(session, company_name)

        if len(companies):
            # List matching companies
            company_selection = {}
            for i, company in enumerate(companies):
                company_selection[i] = {
                    'ticker': company.ticker, 'name': company.name
                }
                print(f'{i} {company.name}')

            # Ask for a company number
            company_number = int(input('Enter company number:\n'))
            company = company_selection[company_number]

            # Ask for company-related values
            values = CrudMenu.get_financial_input()

            # Update the values in the database
            database.update_financial_by_ticker(session, company['ticker'], values)

            session.commit()

            print('Company updated successfully!')
        else:
            print('Company not found!')

    @staticmethod
    def delete_company(session):
        # Ask for a company name
        company_name = input('Enter company name:\n')

        # Search the database for the company name
        companies = database.get_company_by_name(session, company_name)

        if len(companies):
            # List matching companies
            company_selection = {}
            for i, company in enumerate(companies):
                company_selection[i] = {
                    'ticker': company.ticker, 'name': company.name
                }
                print(f'{i} {company.name}')

            # Ask for a company number
            company_number = int(input('Enter company number:\n'))
            company = company_selection[company_number]

            # Delete the company from the database
            database.delete_company(session, company['ticker'])

            print('Company deleted successfully!')

    @staticmethod
    def list_companies(session):
        print('COMPANY LIST')
        companies = database.get_company_list(session)

        for company in companies:
            print(f'{company.ticker} {company.name} {company.sector}')

    def action(self, option, session):
        if not self.isvalid_option(option):
            print('Invalid option!')
        else:
            if option == 1:
                CrudMenu.create_company(session)
            elif option == 2:
                CrudMenu.read_company(session)
            elif option == 3:
                CrudMenu.update_company(session)
            elif option == 4:
                CrudMenu.delete_company(session)
            elif option == 5:
                CrudMenu.list_companies(session)


class TopTenMenu(Menu):
    """Class that represents the top ten menu."""

    MENU = {
        0: 'Back',
        1: 'List by ND/EBITDA',
        2: 'List by ROE',
        3: 'List by ROA',
    }

    def __init__(self):
        super().__init__(TopTenMenu.MENU)

    def __str__(self):
        return super().__str__('TOP TEN MENU')

    def action(self, option, session):
        if not self.isvalid_option(option):
            print('Invalid option!')
        else:
            if option == 1:
                indicator_name = 'ND/EBITDA'
            elif option == 2:
                indicator_name = 'ROE'
            elif option == 3:
                indicator_name = 'ROA'
            else:
                raise NotImplementedError

            ranking = []

            companies_data = database.get_financial(session)
            for company_data in companies_data:
                # Calculate indicators
                indicator = get_indicators(company_data)[indicator_name]
                if indicator is None:
                    indicator = 0

                # Add selected indicator to the ranking
                ranking.append((company_data.ticker, indicator))

            # Sort the ranking
            ranking.sort(key=lambda x: x[1], reverse=True)

            # Take only the first ten elements
            ranking = ranking[:10]

            # Display the top ten
            print(f'TICKER {indicator_name}')
            for ticker, value in ranking:
                print(f'{ticker} {value}')


class InvestorCalculator:
    """Class that represents Calculator for Investors system."""

    def __init__(self, db_filepath='investor.db'):
        print('Welcome to the Investor Program!')
        self.session = create_session(db_filepath)

    def initialize(self):
        for row in companies_df.itertuples():
            entry = {
                'ticker': row[1],
                'name': row[2],
                'sector': row[3]
            }
            database.add_entry(self.session, 'companies', entry)

        for row in financial_df.itertuples():
            entry = {
                'ticker': row[1],
                'ebitda': row[2],
                'sales': row[3],
                'net_profit': row[4],
                'market_price': row[5],
                'net_debt': row[6],
                'assets': row[7],
                'equity': row[8],
                'cash_equivalents': row[9],
                'liabilities': row[10],
            }
            database.add_entry(self.session, 'financial', entry)

        self.session.commit()
        # print('Database created successfully!')

    def get_option(self):
        """Ask user for action and execute it."""
        while True:
            print()
            print(MainMenu())
            try:
                option = int(input('Enter an option:\n'))
            except ValueError:
                print('Invalid option!')
            else:
                if not MainMenu().isvalid_option(option):
                    print('Invalid option!')
                else:
                    if option == 0:
                        print('Have a nice day!')
                        break
                    elif option == 1:
                        self.get_crud_option()
                    elif option == 2:
                        self.get_top_ten_option()
                    else:
                        raise NotImplementedError

    def get_crud_option(self):
        """Ask a user for an option from the CRUD menu."""
        print()
        print(CrudMenu())
        CrudMenu().action(int(input('Enter an option:\n')), self.session)

    def get_top_ten_option(self):
        """Ask a user for an option from the top ten menu."""
        print()
        print(TopTenMenu())

        TopTenMenu().action(int(input('Enter an option:\n')), self.session)


# Set paths to data files
companies_filepath = r'test/companies.csv'
financial_filepath = r'test/financial.csv'

# Read data
companies_df = pd.read_csv(r'raw_data/companies.csv')
financial_df = pd.read_csv(r'raw_data/financial.csv')

calculator = InvestorCalculator('investor.db')
# calculator.initialize()
calculator.get_option()
