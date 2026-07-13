import os
import sys

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.tools.weather_tool import get_weather
from app.tools.time_tool import get_current_time
from app.tools.calculator_tool import calculate
from app.tools.location_tool import get_location_information

def run_tests():
    print("=" * 60)
    print("RUNNING STAGE 1 TOOL TESTS")
    print("=" * 60)

    # 1. Weather Tool Tests
    print("\n--- 1. Weather Tool ---")
    print("Test Normal (Bengaluru):", get_weather("Bengaluru"))
    print("Test Invalid (xyz-invalid-city):", get_weather("xyz-invalid-city"))
    print("Test Empty:", get_weather(""))

    # 2. Time Tool Tests
    print("\n--- 2. Time Tool ---")
    print("Test Normal (Tokyo):", get_current_time("Tokyo"))
    print("Test Invalid (Unknown Location):", get_current_time("Unknown Location xyz"))
    print("Test Empty:", get_current_time(""))

    # 3. Calculator Tool Tests
    print("\n--- 3. Calculator Tool ---")
    print("Test Normal (45000 * 18 / 100):", calculate("45000 * 18 / 100"))
    print("Test Unsafe (eval attempts):", calculate("__import__('os').system('dir')"))
    print("Test Division by Zero (10 / 0):", calculate("10 / 0"))
    print("Test Invalid expression (45 *):", calculate("45 *"))

    # 4. Location Tool Tests
    print("\n--- 4. Location Tool ---")
    print("Test Normal (Eiffel Tower):", get_location_information("Eiffel Tower"))
    print("Test Invalid (xyz-unknown-place):", get_location_information("xyz-unknown-place"))
    print("Test Empty:", get_location_information(""))

    print("\n" + "=" * 60)
    print("STAGE 1 TOOL TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
