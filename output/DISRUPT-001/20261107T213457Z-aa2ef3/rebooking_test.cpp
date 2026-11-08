#include <gtest/gtest.h>
#include "rebooking.hpp"

using namespace std;

TEST(Rebooking, AlternativeFlightNotProposedAfterCancellation)
{
  // Arrange: Cancelled flight AF123 from CDG to FCO at 10:00 UTC (600 minutes)
  Flight cancelledFlight = {
    "AF123",
    "CDG",
    "FCO",
    600,  // 10:00 UTC
    0
  };

  // Candidate flight AF456 from CDG to FCO at 14:00 UTC (840 minutes) with 2 available seats
  Flight candidateFlight = {
    "AF456",
    "CDG",
    "FCO",
    840,  // 14:00 UTC
    2
  };

  vector<Flight> candidates = {candidateFlight};

  // Act: Call findAlternative with cancelled flight and candidates
  auto result = findAlternative(cancelledFlight, candidates);

  // Assert: Expected AF456 to be returned as alternative
  ASSERT_TRUE(result.has_value());
  EXPECT_EQ(result->id, "AF456");
  EXPECT_EQ(result->from, "CDG");
  EXPECT_EQ(result->to, "FCO");
  EXPECT_EQ(result->departure_minutes, 840);
  EXPECT_EQ(result->available_seats, 2);
}

TEST(Rebooking, NoAlternativeWhenDepartureNotStrictlyAfterCancelled)
{
  // Arrange: Cancelled flight AF123 from CDG to FCO at 10:00 UTC (600 minutes)
  Flight cancelledFlight = {
    "AF123",
    "CDG",
    "FCO",
    600,  // 10:00 UTC
    0
  };

  // Candidate flight AF456 from CDG to FCO at 10:00 UTC (same time) - not strictly after
  Flight candidateFlight = {
    "AF456",
    "CDG",
    "FCO",
    600,  // 10:00 UTC - same as cancelled
    2
  };

  vector<Flight> candidates = {candidateFlight};

  // Act: Call findAlternative with cancelled flight and candidates
  auto result = findAlternative(cancelledFlight, candidates);

  // Assert: No alternative expected since departure is not strictly after cancelled flight
  EXPECT_FALSE(result.has_value());
}

TEST(Rebooking, NoAlternativeWhenDifferentAirport)
{
  // Arrange: Cancelled flight AF123 from CDG to FCO at 10:00 UTC (600 minutes)
  Flight cancelledFlight = {
    "AF123",
    "CDG",
    "FCO",
    600,  // 10:00 UTC
    0
  };

  // Candidate flight AF456 from CDG to MXP at 14:00 UTC (different destination)
  Flight candidateFlight = {
    "AF456",
    "CDG",
    "MXP",
    840,  // 14:00 UTC
    2
  };

  vector<Flight> candidates = {candidateFlight};

  // Act: Call findAlternative with cancelled flight and candidates
  auto result = findAlternative(cancelledFlight, candidates);

  // Assert: No alternative expected since destination is different
  EXPECT_FALSE(result.has_value());
}

TEST(Rebooking, NoAlternativeWhenNoAvailableSeats)
{
  // Arrange: Cancelled flight AF123 from CDG to FCO at 10:00 UTC (600 minutes)
  Flight cancelledFlight = {
    "AF123",
    "CDG",
    "FCO",
    600,  // 10:00 UTC
    0
  };

  // Candidate flight AF456 from CDG to FCO at 14:00 UTC with 0 available seats
  Flight candidateFlight = {
    "AF456",
    "CDG",
    "FCO",
    840,  // 14:00 UTC
    0
  };

  vector<Flight> candidates = {candidateFlight};

  // Act: Call findAlternative with cancelled flight and candidates
  auto result = findAlternative(cancelledFlight, candidates);

  // Assert: No alternative expected since no available seats
  EXPECT_FALSE(result.has_value());
}

TEST(Rebooking, SelectEarliestDepartureWhenMultipleCandidates)
{
  // Arrange: Cancelled flight AF123 from CDG to FCO at 10:00 UTC (600 minutes)
  Flight cancelledFlight = {
    "AF123",
    "CDG",
    "FCO",
    600,  // 10:00 UTC
    0
  };

  // Two candidate flights with same route and time
  Flight candidateFlight1 = {
    "AF456",
    "CDG",
    "FCO",
    840,  // 14:00 UTC
    2
  };

  Flight candidateFlight2 = {
    "AF789",
    "CDG",
    "FCO",
    840,  // 14:00 UTC - same time as AF456
    3
  };

  vector<Flight> candidates = {candidateFlight1, candidateFlight2};

  // Act: Call findAlternative with cancelled flight and candidates
  auto result = findAlternative(cancelledFlight, candidates);

  // Assert: AF456 should be selected (lexicographically first when times are tied)
  ASSERT_TRUE(result.has_value());
  EXPECT_EQ(result->id, "AF456");
}
