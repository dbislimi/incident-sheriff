#include <gtest/gtest.h>
#include "rebooking.hpp"

TEST(Rebooking, UnknownFlightIdReturnsNoAlternative) {
  Flight cancelledFlight;
  cancelledFlight.id = "FL-999";
  cancelledFlight.from = "JFK";
  cancelledFlight.to = "LAX";
  cancelledFlight.departure_minutes = 600;
  cancelledFlight.available_seats = 0;

  std::vector<Flight> candidates;
  candidates.push_back({"FL-100", "JFK", "SFO", 720, 5});
  candidates.push_back({"FL-101", "ORD", "LAX", 840, 3});

  auto result = findAlternative(cancelledFlight, candidates);

  EXPECT_FALSE(result.has_value());
}

TEST(Rebooking, ValidFlightIdReturnsEarliestCandidate) {
  Flight cancelledFlight;
  cancelledFlight.id = "FL-100";
  cancelledFlight.from = "JFK";
  cancelledFlight.to = "LAX";
  cancelledFlight.departure_minutes = 600;
  cancelledFlight.available_seats = 5;

  std::vector<Flight> candidates;
  candidates.push_back({"FL-101", "JFK", "SFO", 720, 5});
  candidates.push_back({"FL-102", "JFK", "LAX", 840, 3});

  auto result = findAlternative(cancelledFlight, candidates);

  ASSERT_TRUE(result.has_value());
  EXPECT_EQ(result->id, "FL-101");
  EXPECT_EQ(result->from, "JFK");
  EXPECT_EQ(result->to, "SFO");
  EXPECT_EQ(result->departure_minutes, 720);
}