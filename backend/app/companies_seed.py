"""
The 20 large-cap NSE companies FinPulse tracks.
`ticker` is the yfinance symbol (NSE tickers need the .NS suffix).
Kept as static data (not fetched live) so ingestion doesn't depend on
yfinance returning good description text, which is unreliable.
"""

COMPANIES = [
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy & Conglomerate",
     "description": "India's largest private company, spanning oil & gas, petrochemicals, retail, and telecom (Jio)."},
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services", "sector": "IT Services",
     "description": "India's largest IT services and consulting firm, part of the Tata Group."},
    {"ticker": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking",
     "description": "India's largest private sector bank by assets and market capitalization."},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking",
     "description": "Major private sector bank offering retail and corporate banking services."},
    {"ticker": "INFY.NS", "name": "Infosys", "sector": "IT Services",
     "description": "Global IT consulting and services company headquartered in Bengaluru."},
    {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG",
     "description": "India's largest fast-moving consumer goods company, subsidiary of Unilever."},
    {"ticker": "ITC.NS", "name": "ITC Limited", "sector": "FMCG & Conglomerate",
     "description": "Diversified conglomerate with interests in FMCG, hotels, paper, and agribusiness."},
    {"ticker": "SBIN.NS", "name": "State Bank of India", "sector": "Banking",
     "description": "India's largest public sector bank by assets."},
    {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom",
     "description": "One of India's leading telecommunications service providers."},
    {"ticker": "LT.NS", "name": "Larsen & Toubro", "sector": "Engineering & Construction",
     "description": "Major engineering, construction, and infrastructure conglomerate."},
    {"ticker": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Banking",
     "description": "Private sector bank offering banking, financial services, and insurance."},
    {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "NBFC",
     "description": "Leading non-banking financial company offering consumer and business lending."},
    {"ticker": "HCLTECH.NS", "name": "HCL Technologies", "sector": "IT Services",
     "description": "Global technology company providing IT services and engineering solutions."},
    {"ticker": "ASIANPAINT.NS", "name": "Asian Paints", "sector": "Consumer Goods",
     "description": "India's largest paint and home decor company."},
    {"ticker": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Automobile",
     "description": "India's largest passenger vehicle manufacturer."},
    {"ticker": "AXISBANK.NS", "name": "Axis Bank", "sector": "Banking",
     "description": "Third-largest private sector bank in India."},
    {"ticker": "SUNPHARMA.NS", "name": "Sun Pharmaceutical", "sector": "Pharmaceuticals",
     "description": "India's largest pharmaceutical company by revenue."},
    {"ticker": "TITAN.NS", "name": "Titan Company", "sector": "Consumer Goods",
     "description": "Watches, jewellery, and eyewear company, part of the Tata Group."},
    {"ticker": "TATAMOTORS.NS", "name": "Tata Motors", "sector": "Automobile",
     "description": "Automobile manufacturer producing passenger and commercial vehicles, owns Jaguar Land Rover."},
    {"ticker": "ADANIENT.NS", "name": "Adani Enterprises", "sector": "Conglomerate",
     "description": "Flagship company of the Adani Group, incubating new businesses across sectors."},
]
