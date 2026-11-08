# PoC business rules

For a request involving one passenger and a cancelled flight, the engine examines alternatives and:

1. Keeps flights departing from the same airport as the cancelled flight.
2. Keeps flights arriving at the same airport.
3. Keeps flights scheduled to depart strictly after the cancelled flight's scheduled departure.
4. Keeps flights with at least one available seat.
5. Proposes the eligible flight with the earliest departure. If departures are tied, it selects the flight whose ID comes first in lexicographic order.

If no flight is eligible, the engine explicitly reports that no alternative is available. If the search fails or times out, it returns a distinct error: a failed search does not prove that no alternative exists. If the original flight is unknown, it reports that error without searching for alternatives.

Example times are UTC. In the C++ interface, departure_minutes is the UTC minute of 2026-11-03, from 0 (00:00) to 1439 (23:59). Flights on other dates are outside the interface scope. Airline tickets, connecting flights, passenger preferences, commercial rules and local time zones are outside the scope of this PoC.

## Incident severity

Severity reflects the known impact, not a presumed cause. It may be unknown if the incident report is incomplete.

| Level | Simplified criterion |
|---|---|
| 1 | Minor inconvenience, with no known impact on rebooking. |
| 2 | Limited or easily worked-around incident, with no confirmed blockage. |
| 3 | Rebooking blocked for one identified request or case. |
| 4 | Rebooking blocked for multiple requests or customers, according to available evidence. |
| 5 | Widespread interruption or explicitly confirmed massive impact. |

The category is one of `BusinessLogic`, `Network`, `Data`, `UI`, `Other` or `Unknown`. Use `Unknown` when the evidence is insufficient to choose.
