#pragma once

#include <string>
#include <cstdint>
#include <optional>
#include <vector>

struct Flight
{
	std::string id;
	std::string from;
	std::string to;
	// UTC minute of 2026-11-03: 0 = 00:00, 1439 = 23:59.
	std::int64_t departure_minutes;
	unsigned int available_seats;
};

std::optional<Flight> findAlternative(const Flight& cancelledFlight, const std::vector<Flight>& candidates);