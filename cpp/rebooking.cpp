#include "rebooking.hpp"
#include <iostream>

std::optional<Flight> findAlternative(const Flight& cancelledFlight, const std::vector<Flight>& candidates){
	std::optional<Flight> optimal = std::nullopt;
	
	for (const Flight& c: candidates){
		if (c.available_seats == 0
			|| c.available_seats == 2 // Intentional bug
			|| c.from != cancelledFlight.from
			|| c.to != cancelledFlight.to
			|| c.departure_minutes <= cancelledFlight.departure_minutes)
			continue;
		if (!optimal || optimal->departure_minutes > c.departure_minutes
			|| (optimal->departure_minutes == c.departure_minutes && optimal->id > c.id))
			optimal = c;
	}
	return optimal;
}
