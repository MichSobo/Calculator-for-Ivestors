"""
Code for interaction with a database, which uses Object Relational Mapping
concept with declarative mapping.

Procedure:
    1. Connect to database (create SQLAlchemy engine).
    2. Declare mapping classes.
    3. Create a schema (tables).
    4. Create a Session (ORM's handle to the database).
"""
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Query

Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'

    ticker = Column(String(10), primary_key=True)
    name = Column(String(50))
    sector = Column(String(50))

    def __repr__(self):
        return f'<Company(ticker={self.ticker}, ' \
               f'name={self.name}, ' \
               f'sector={self.sector})>'


class Financial(Base):
    __tablename__ = 'financial'

    ticker = Column(String(10), primary_key=True)
    ebitda = Column(Float)
    sales = Column(Float)
    net_profit = Column(Float)
    market_price = Column(Float)
    net_debt = Column(Float)
    assets = Column(Float)
    equity = Column(Float)
    cash_equivalents = Column(Float)
    liabilities = Column(Float)


def connect(db_filepath='database.db'):
    """Return a handle to the core interface to the database."""
    engine = create_engine(f'sqlite:///{db_filepath}', echo=False)

    return engine


def create_tables(engine):
    """Create a database schema."""
    Base.metadata.create_all(engine)


def create_session(engine):
    """Return an ORM's handle to the database."""
    Session = sessionmaker(bind=engine, autoflush=False)

    return Session()


def add_entry(session, table, values, do_commit=False):
    """Add an entry to the selected table."""
    if table == 'companies':
        entry = Company(**values)
    elif table == 'financial':
        entry = Financial(**values)
    else:
        raise NotImplementedError

    session.add(entry)

    if do_commit:
        session.commit()


def get_company_by_name(session, name):
    """Return a list with companies that match the name."""
    query = session.query(Company.ticker, Company.name)
    query = query.filter(Company.name.like(f'%{name}%'))

    companies = [entry for entry in query]
    return companies


def get_financial_by_ticker(session, ticker):
    """Return financial data for the selected company ticker."""
    query = session.query(Financial)
    query = query.filter(Financial.ticker == ticker)

    return query[0]


def get_financial(session):
    """Return financial data for all companies in the database."""
    query = session.query(Financial)

    companies = [entry for entry in query]

    return companies


def update_financial_by_ticker(session, ticker, values, do_commit=False):
    """Update an entry in `financial` table with new values."""
    query = session.query(Financial)
    query = query.filter(Financial.ticker == ticker)

    query.update(values)

    if do_commit:
        session.commit()


def delete_company(session, ticker):
    """Delete a company from the database."""
    session.query(Company).filter(Company.ticker == ticker).delete()
    session.query(Financial).filter(Financial.ticker == ticker).delete()

    session.commit()


def get_company_list(session, do_sort=True):
    """Return a list of all companies in the database."""
    query = session.query(Company.ticker, Company.name, Company.sector)

    companies = [entry for entry in query]

    if do_sort:
        companies.sort(key=lambda x: x.ticker)

    return companies
