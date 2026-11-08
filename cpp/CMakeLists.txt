cmake_minimum_required(VERSION 3.14)
project(disruption_sheriff LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(TEST_SOURCE_FILE "rebooking_test.cpp" CACHE FILEPATH "test_path")

enable_testing()
find_package(GTest REQUIRED)

add_executable(rebooking_tests
	rebooking.cpp
	${TEST_SOURCE_FILE}
)

target_include_directories(rebooking_tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(rebooking_tests PRIVATE GTest::gtest_main)

option(DISCOVER_TESTS "Discover Google Test cases after building" ON)
if(DISCOVER_TESTS)
	include(GoogleTest)
	gtest_discover_tests(rebooking_tests)
endif()
