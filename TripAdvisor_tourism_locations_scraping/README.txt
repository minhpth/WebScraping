HOW TO SET UP TEST CASES

1. Create some test cases from test_cases.sh

#!/bin/sh
python TripAdvisor_scraping.py "Ha Noi, Viet Nam"
python TripAdvisor_scraping.py "Ho Chi Minh City, Viet Nam"
python TripAdvisor_scraping.py "Hue, Vietnam"
python TripAdvisor_scraping.py "Paris"
python TripAdvisor_scraping.py "France"
python TripAdvisor_scraping.py "Nice, France"
python TripAdvisor_scraping.py "London"
python TripAdvisor_scraping.py "UK"
python TripAdvisor_scraping.py "New York"
python TripAdvisor_scraping.py "Belgium"

2. Run the test

Make the test_cases.sh runable
$ chmod +x test_cases.sh

Run the file by
./test_cases.sh

Refs: http://stackoverflow.com/questions/4377109/shell-script-execute-a-python-program-from-within-a-shell-script
