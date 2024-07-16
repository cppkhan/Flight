import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'
import { format } from 'date-fns';

const App = () => {
  const [flights, setFlights] = useState([]);
  const [destination, setDestination] = useState('');
  const [airlines, setAirlines] = useState('');
  const fetchFlights = async () => {
    try {
    //  var url = 'http://127.0.0.1:5000/flights';
     var url = "https://2zfayfx8f6.execute-api.eu-north-1.amazonaws.com/dev/flights"
    console.log(destination,airlines.length);
      if (destination || airlines.length > 0) {
       const params = new URLSearchParams();
        if (destination) params.append('destination', destination);
        if (airlines.length > 0) params.append('airlines', airlines.join(','));
        url += `?${params.toString()}`;
        console.log(url)

      }
       const response = await axios.get(url);
      setFlights(response.data);
      console.log(response)
    } catch (error) {
      console.error('Error fetching flights:', error);
    }
  };
const FlightView=()=>{
  return(
          <ul>
 {(destination&&airlines&&flights.length>0)?flights.map(flight => (
  <div className='flight-container' key={flight.id}>
<div className="heading-flight">
  <div className="flight-detail">
    <span className="label">Flight Number</span>
    <span className="value">{flight.flight_number}</span>
  </div>
  <div className="flight-detail">
    <span className="label">Airline</span>
    <span className="value">{flight.airline}</span>
  </div>
  <div className="flight-detail">
    <span className="label">Origin</span>
    <span className="value">{flight.origin}</span>
  </div>
  <div className="flight-detail">
    <span className="label">Destination</span>
    <span className="value">{flight.destination}</span>
  </div>
  <div className="flight-detail">
    <span className="label">Scheduled Departure</span>
    <span className="value">{format(flight.scheduled_departure_at, "yyyy-MM-dd'T  'HH:mm").split('T')}</span>
  </div>
  <div className="flight-detail">
    <span className="label">Actual Departure</span>
    <span className="value">{format(flight.actual_departure_at, "yyyy-MM-dd'T  'HH:mm").split('T')}</span>
  </div>
</div>

   <div>

           {flight?.delays.length>0&&  <span className='label delays-label'> Delays:</span> }
      
                 {flight?.delays.map(delay => (
                   <ul className='delays-container' key={delay.code}>
                    
                    <div className=' description-container time-container'>
                    <span className="label">Time: </span>
                    <span>{delay.time_minutes} minutes</span>
                    </div>
                    <div className='description-container'>
                     <span className='label'>Description:</span>
                     <span>{delay.description}</span>
                     </div>
                     <hr></hr>
                   </ul>
                 ))}
         
             </div>

  </div>
        )):<div className='nothing-container'>
          <span >Nothing to show........</span>
          </div> }

      </ul>
  )
}
const TextFeild=()=>{
  return(
          <form   onSubmit={(e) => { e.preventDefault() }}>
        <div className="Form-inner">
        <label  className='text-label' htmlFor="destination">Destination*:</label>
        <input
          type="text"
          id="destination"
         
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          required
        />
        <label className='text-label' htmlFor="airlines">Airlines*:</label>
        <input
          type="text"
          id="airlines"
          value={airlines}
          onChange={(e) => setAirlines(e.target.value.split(','))}
          required
        />
        </div>
        <button className='button-style' type="submit" onClick={()=>(destination&&airlines)?fetchFlights():null} >Search</button>
      </form>
  )
}
  return (
    <div className="container">
      <h1 className='Header-color'>Flight Information</h1>
{TextFeild()}
{FlightView()}
    </div>
  );
};

export default App;

