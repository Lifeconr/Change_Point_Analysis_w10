//  dashboard/src/components/EventList.js
import React from 'react';

const EventList = ({ events, onEventClick }) => {
  if (!events || events.length === 0) {
    return <p className="no-events-text">No events to display.</p>;
  }

  return (
    <div className="table-container">
      <table className="event-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Event</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event, index) => (
            <tr
              key={index}
              onClick={() => onEventClick(event)}
            >
              <td>{event.Date}</td>
              <td className="event-name">{event.Event}</td>
              <td>{event.Description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default EventList;
