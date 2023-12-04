from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime as dt

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Home Route
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
#Parecipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session (link) from Python to the DB
    session = Session(engine)
    # Query for the dates and precipitation values
    results = session.query(Measurement.date, Measurement.prcp).all()
    # Close the session
    session.close()
    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)


#Stations Route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Determine the most active station ID (replace this with your logic to find the most active station)
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).\
                          first()[0]

    # Find the last date of observation for the most active station
    latest_date = session.query(Measurement.date).\
                  filter(Measurement.station == most_active_station).\
                  order_by(Measurement.date.desc()).\
                  first()[0]
    one_year_ago = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query for the dates and temperature observations from a year from the last data point for this station
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= one_year_ago).all()

    # Close the session
    session.close()

    # Create a dictionary from the row data and append to a list of temperature observations
    temperatures = {date: tobs for date, tobs in results}

    return jsonify(temperatures)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    # Query for the min, avg, and max temperatures from the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary for the results
    temp_data = {'TMIN': results[0][0], 'TAVG': results[0][1], 'TMAX': results[0][2]}

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)

    # Query for the min, avg, and max temperatures between the start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Create a dictionary for the results
    temp_data = {'TMIN': results[0][0], 'TAVG': results[0][1], 'TMAX': results[0][2]}

    return jsonify(temp_data)

# Flask App Run
if __name__ == '__main__':
    app.run(debug=True)
