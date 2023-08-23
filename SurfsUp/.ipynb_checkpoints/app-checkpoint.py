# Import the dependencies.

from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct 
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    return ("""
        <h1> Alejandro Davila - UTA_DATA Module 10 </h1>
        <h3> Available Routes for Hawaii Weather Data: </h3>
        
        <ul>
        
        <li><a href = "/api/v1.0/precipitation_totals_by_day"> Precipitation</a>: <strong>/api/v1.0/precipitation_totals_by_day</strong> </li><br/>
        <li><a href = "/api/v1.0/stations"> Stations </a>: <strong>/api/v1.0/stations</strong></li><br/>
        <li><a href = "/api/v1.0/tobs_USC00519281"> TOBS_USC00519281 </a>: <strong>/api/v1.0/tobs_USC00519281</strong></li><br/>
        
        <li>To retrieve the minimum, average, and maximum temperatures for a specific start date, use <strong>/api/v1.0/&ltstart_date&gt</strong> (replace start date in yyyy-mm-dd format)</li>
            Use this link to see an example for date 2016-08-23:<a href = "/api/v1.0/2016-08-23"> /api/v1.0/2016-08-23 </a><br/><br/>
        
        <li>To retrieve the minimum, average, and maximum temperatures for a specific start-end range, use <strong>/api/v1.0/&ltstart_date&gt/&ltend_date&gt</strong> (replace start and end date in yyyy-mm-dd format)</li>
            Use this link to see a range example for dates 2016-09-01/2016-09-30:<a href = "/api/v1.0/2016-09-01/2016-09-30"> /api/v1.0/2016-09-01/2016-09-30 </a><br/><br/>
        </ul> 
        
        """   
        f"NOTE: If no end-date is provided, the trip api calculates stats through 08/23/2017")   
        




#################################################
# PRECIPITATION
#################################################

@app.route("/api/v1.0/precipitation_totals_by_day")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all daily precipitation totals for the last year"""
    # Query and summarize daily precipitation across all stations for the last year of available data
    
    querydate = '2016-08-23'
    precipitation_scrs = [measurement.date,func.sum(measurement.prcp)]
    
    queryresult = session.query(*precipitation_scrs).filter(measurement.date >= querydate).group_by(measurement.date).order_by(measurement.date).all()
    
    session.close()


# Return a dictionary with the date as key and the daily precipitation total as value
    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in queryresult:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))
    return jsonify(precipitation_dict)





#################################################
# STATIONS
#################################################

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all the active Weather stations in Hawaii"""
    # Return a list of active weather stations in Hawaii
    asc = [measurement.station]
    station_temp_summary = session.query(*asc).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    session.close()

    # Return a dictionary with the date as key and the daily precipitation total as value
    # Convert list of tuples into normal list and return the JSonified list
    list_of_stations = list(np.ravel(station_temp_summary)) 
    
    return jsonify(list_of_stations)




#################################################
# TOBS
#################################################

@app.route("/api/v1.0/tobs_USC00519281")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the last 12 months of temperature observation data for the most active station
    start_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    # Return a dictionary with the date as key and the daily temperature observation as value
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)





#################################################
# DATES
#################################################

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def cal_temp(start=None, end=None):
    # Create the session
    session = Session(engine)
    
    # Make a list to query (the minimum, average and maximum temperature)
    asc=[func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    # Check if there is an end date then do the task accordingly
    if end == None: 
        # Query the data from start date to the most recent date
        start_data = session.query(*asc).\
                            filter(measurement.date >= start).all()
        # Convert list of tuples into normal list
        start_list = list(np.ravel(start_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start date
        return jsonify(start_list)
    else:
        # Query the data from start date to the end date
        start_end_data = session.query(*asc).\
                            filter(measurement.date >= start).\
                            filter(measurement.date <= end).all()
        # Convert list of tuples into normal list
        start_end_list = list(np.ravel(start_end_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start-end date range
        return jsonify(start_end_list)

    # Close the session                   
    session.close()
    
  

if __name__ == '__main__':
    app.run(debug=True,port=5002)