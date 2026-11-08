#include <gtest/gtest.h>
#include "rebooking.hpp"

TEST(Rebooking, AlternativeFlightShouldBeProposed) {
  // Arrange
  Flight cancelledFlight;
  cancelledFlight.id = "AF123";
  cancelledFlight.from = "CDG";
  cancelledFlight.to = "FCO";
  cancelledFlight.departure_minutes = 600; // 10:00 UTC
  
  std::vector<Flight> candidates;
  Flight candidate;
  candidate.id = "AF456";
  candidate.from = "CDG";
  candidate.to = "FCO";
  candidate.departure_minutes = 840; // 14:00 UTC
  candidate.available_seats = 2;
  
  candidates.push_back(candidate);
  
  // Act
  auto result = findAlternative(cancelledFlight, candidates);
  
  // Assert
  ASSERT_TRUE(result.has_value());
  EXPECT_EQ(result->id, "AF456");
  EXPECT_EQ(result->from, "CDG");
  EXPECT_EQ(result->to, "FCO");
  EXPECT_EQ(result->departure_minutes, 840);
  EXPECT_EQ(result->available_seats, 2);
}

TEST(Rebooking, AlternativeFlightSelectedEarliestDeparture) {
  // Arrange
  Flight cancelledFlight;
  cancelledFlight.id = "AF123";
  cancelledFlight.from = "CDG";
  cancelledFlight.to = "FCO";
  cancelledFlight.departure_minutes = 600; // 10:00 UTC
  
  std::vector<Flight> candidates;
  Flight candidate1;
  candidate1.id = "AF456";
  candidate1.from = "CDG";
  candidate1.to = "FCO";
  candidate1.departure_minutes = 840; // 14:00 UTC
  candidate1.available_seats = 2;
  
  Flight candidate2;
  candidate2.id = "AF789";
  candidate2.from = "CDG";
  candidate2.to = "FCO";
  candidate2.departure_minutes = 840; // 14:00 UTC
  candidate2.available_seats = 5;
  
  candidates.push_back(candidate1);
  candidates.push_back(candidate2);
  
  // Act
  auto result = findAlternative(cancelledFlight, candidates);
  
  // Assert
  ASSERT_TRUE(result.has_value());
  EXPECT_EQ(result->id, "AF456");
}

TEST(Rebooking, AlternativeFlightRequiresLaterDeparture) {
  // Arrange
  Flight cancelledFlight;
  cancelledFlight.id = "AF123";
  cancelledFlight.from = "CDG";
  cancelledFlight.to = "FCO";
  cancelledFlight.departure_minutes = 840; // 14:00 UTC
  
  std::vector<Flight> candidates;
  Flight candidate;
  candidate.id = "AF456";
  candidate.from = "CDG";
  candidate.to = "FCO";
  candidate.departure_minutes = 600; // 10:00 UTC (before cancelled)
  candidate.available_seats = 2;
  
  candidates.push_back(candidate);
  
  // Act
  auto result = findAlternative(cancelledFlight, candidates);
  
  // Assert
  ASSERT_TRUE(result.has_value());
  EXPECT_FALSE(result.has_value());
}

TEST(Rebooking, AlternativeFlightRequiresAvailableSeats) {
  // Arrange
  Flight cancelledFlight;
  cancelledFlight.id = "AF123";
  cancelledFlight.from = "CDG";
  cancelledFlight.to = "FCO";
  cancelledFlight.departure_minutes = 600; // 10:00 UTC
  
  std::vector<Flight> candidates;
  Flight candidate;
  candidate.id = "AF456";
  candidate.from = "CDG";
  candidate.to = "FCO";
  candidate.departure_minutes = 840; // 14:00 UTC
  candidate.available_seats = 0;
  
  candidates.push_back(candidate);
  
  // Act
  auto result = findAlternative(cancelledFlight, candidates);
  
  // Assert
  ASSERT_TRUE(result.has_value());
  EXPECT_FALSE(result.has_value());
}

TEST(Rebooking, NoAlternativeWhenNoneEligible) {
  // Arrange
  Flight cancelledFlight;
  cancelledFlight.id = "AF123";
  cancelledFlight.from = "CDG";
  cancelledFlight.to = "FCO";
  cancelledFlight.departure_minutes = 600; // 10:00 UTC
  
  std::vector<Flight> candidates;
  Flight candidate;
  candidate.id = "AF456";
  candidate.from = "CDG";
  candidate.to = "FCO";
  candidate.departure_minutes = 840; // 14:00 UTC
  candidate.available_seats = 2;
  
  candidates.push_back(candidate);
  
  // Act
  auto result = findAlternative(cancelledFlight, candidates);
  
  // Assert
  ASSERT_TRUE(result.has_value());
  EXPECT_FALSE(result.has_value());
}