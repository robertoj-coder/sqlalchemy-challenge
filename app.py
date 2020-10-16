import numpy as np
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import datetime as dt
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import sqlite3

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)
# Base.classes.keys()


Measurement = Base.classes.measurement
Station = Base.classes.station


# session = Session(engine)


app = Flask(__name__)

@app.route("/")
def home():
    return(
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end>"
)
# Convert the query results to a dictionary using date as the key and prcp as the value.


# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    preci_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>="2016-08-23").all()

    session.close()
    
    preci_dict = {}
    for result in preci_data:
        preci_dict[result[0]] = result[1]


    return jsonify(preci_dict)
# Query the dates and temperature observations of the most active station for the last year of data.


# Return a JSON list of temperature observations (TOBS) for the previous year.


@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    stat_info = session.query(Station.station, Station.name).all()
    session.close()
    stat_list = list(np.ravel(stat_info))

    return jsonify(stat_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # temp_info = session.query(Measurement.date, Measurement.tobs).\
    #         filter(Measurement.date>="2016-08-23").all()
    temp_info = (session.query(Measurement.date,Measurement.tobs)
                          .filter(Measurement.station == "USC00519281")
                          .filter(Measurement.date >= "2016-08-23").all())
    session.close()
    temp_list = list(np.ravel(temp_info))

    return jsonify(temp_list)
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
def begin_date(start):
    
    session = Session(engine)
    
    temp_cal = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    start_temp =  (session.query(*temp_cal)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .group_by(Measurement.date)
                       .all())
    session.close()
    
    dates = []                       
    for i in start_temp:
        start_dict = {}
        start_dict["Date"] = i[0]
        start_dict["TMIN"] = i[1]
        start_dict["TAVG"] = i[2]
        start_dict["TMAX"] = i[3]
        dates.append(start_dict)
        
    return jsonify(dates)   

#  When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def begin_end(start, end):
    session = Session(engine)
    temp_cal = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    



    start_end =  (session.query(*temp_cal).\
                        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
                        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end)
                        .group_by(Measurement.date)
                       .all())
    
    # temps = list(np.ravel(start_end))
    # return jsonify(temps)
    

    dates = []                       
    for i in start_end:
        end_dict = {}
        end_dict["Date"] = i[0]
        end_dict["TMIN"] = i[1]
        end_dict["TAVG"] = i[2]
        end_dict["TMAX"] = i[3]
        dates.append(end_dict)


    return jsonify(dates)
	   
	    


if __name__ == "__main__":
    app.run(debug=True)