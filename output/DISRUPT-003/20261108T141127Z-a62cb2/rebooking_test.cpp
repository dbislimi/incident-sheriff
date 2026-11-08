#include <gtest/gtest.h>
#include "rebooking.hpp"

TEST(Rebooking, UnknownFlightIdReturnsNoValue)
{
  // Arrange: Create a Flight object with an unknown ID that doesn't exist in candidates
  Flight cancelledFlight;
  cancelledFlight.id = "FL-999";
  cancelledFlight.from = "JFK";
  cancelledFlight.to = "LAX";
  cancelledFlight.departure_minutes = 600;
  cancelledFlight.available_seats = 10;

  // Create candidate flights that don't include FL-999
  std::vector<Flight> candidates;
  Flight candidate1;
  candidate1.id = "FL-001";
  candidate1.from = "JFK";
  candidate1.to = "LAX";
  candidate1.departure_minutes = 720;
  candidate1.available_seats = 5;

  candidates.push_back(candidate1);

  // Act: Call findAlternative with the unknown flight
  auto result = findAlternative(cancelledFlight, candidates);

  // Assert: The function should return no value when the original flight is unknown
  EXPECT_FALSE(result.has_value());
}

TEST(Rebooking, ValidFlightIdReturnsEligibleAlternative)
{
  // Arrange: Create a Flight object with a valid ID that exists in candidates
  Flight cancelledFlight;
  cancelledFlight.id = "FL-001";
  cancelledFlight.from = "JFK";
  cancelledFlight.to = "LAX";
  cancelledFlight.departure_minutes = 600;
  cancelledFlight.available_seats = 10;

  // Create candidate flights that include the same flight ID
  std::vector<Flight> candidates;
  Flight candidate1;
  candidate1.id = "FL-002";
  candidate1.from = "JFK";
  candidate1.to = "LAX";
  candidate1.departure_minutes = 720;
  candidate1.available_seats = 5;

  candidates.push_back(candidate1);

  // Act: Call findAlternative with a valid flight ID
  auto result = findAlternative(cancelledFlight, candidates);

  // Assert: The function should return an eligible alternative when the original flight is known
  ASSERT_TRUE(result.has_value());
  EXPECT_EQ((*result).id, "FL-002");
}
