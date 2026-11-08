#include <gtest/gtest.h>
#include "rebooking.hpp"

TEST(Rebooking, ProposesEligibleFlightWithTwoSeats) {
	const std::int64_t cancelled_depart = 600;
	const std::int64_t candidate_depart = 840;

	const Flight a = {.id="AF123", .from="CDG", .to="FCO", .departure_minutes=cancelled_depart, .available_seats=0};
	const Flight b = {.id="AF456", .from="CDG", .to="FCO", .departure_minutes=candidate_depart, .available_seats=2};
	
	const std::vector<Flight> candidates = {b};

	std::optional<Flight> alternative = findAlternative(a, candidates);

	ASSERT_TRUE(alternative.has_value());
	EXPECT_EQ(alternative->id, "AF456");
}