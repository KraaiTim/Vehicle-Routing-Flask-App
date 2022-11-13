import pandas as pd
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim


def read_addresses(file) -> pd.DataFrame:
    file_extension = file.filename.split(".")[-1]
    if file_extension == "csv":
        df = pd.read_csv(file, header=0)
    elif file_extension == "xls" or file_extension == "xlsx":
        df = pd.read_excel(file, header=0)
    else:
        # TODO change to flash message
        print("Incorrect file type")

    # Change column names
    df['ADDRESS'] = df[['Street', 'Number', 'Postcode', 'City',
                        'State', 'Country']].stack().astype(str).groupby(level=0).agg(', '.join)

    geolocator = Nominatim(user_agent="application")

    # 1 second delay between geocoding calls
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    # Apply geocoding
    df['location'] = df['ADDRESS'].apply(geocode)
    # Extract Lat and Long from locations
    df['Lat'] = df['location'].apply(lambda x: x.latitude if x else None)
    df['Lon'] = df['location'].apply(lambda y: y.longitude if y else None)

    return df
