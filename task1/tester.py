import os
import sys
import requests

#####################################
# Definition of tests (see README.md for more thoughts)
tests_short = {
    "correct_path": ["aa", "ab", "AA", "AB", "Aa", "Ab", "11", "12", "a1", "1a", "A1", "1A"],
    "incorrect_path": ["a", "A", "1", "!", "a!", "A!", "1!", "aaa", "aab", "AAA", "AAB", "AAb", "aa1", "a11", "ab1", "a12", "AA1", "A11", "AB1", "A12", "a1!", "A1!"]
}

tests_long = {
    "correct_path": ["aaa", "aab", "AAA", "AAB", "AAa", "AAb", "111", "112", "aa1", "a11", "A11", "AB1", "Aa1"],
    "incorrect_path": ["", "a", "1", "!", "aa", "ab", "AA", "AB", "Aa", "Ab", "11", "12", "a1", "1a", "A1", "1A", "aa!", "ab!", "11!", "12!", "a1!", "aaaa", "aaab", "AAAA", "AAAB", "AB11", "Ab1!"]
}
#######################################

# Set URL variable from env vars or use default one
url = os.environ.get("TEST_URL", "https://ionaapp.com/assignment-magic/dk/")
print(f"Obtained URL: {url}")

# Set API type (short or long) or use "short" as default
api_type = os.environ.get("API_TYPE", "short")
if api_type not in ["short", "long"]:
    print("Incorrect API type: should be 'short' or 'long'")
    sys.exit(1)
print(f"Obtained API type: short")

# Set tests that should be used depending on API type
tests = {}
if api_type == "short":
    tests = tests_short
else:
    tests = tests_long

# Prepare result object for final output
results = {
    "total": len(tests["correct_path"]) + len(tests["incorrect_path"]),
    "passed": 0,
    "failed": []
}

# Function that runs a single test against API endpoint
# Accepts: test_path = path to test,
#          api_type = defines rules for deciding if test passed or failed
def test_api(test_path, api_type):
    # Making request
    response = requests.get(f'{url}/{api_type}/{test_path}')

    # Set up rules for API types
    length = {
        "short": 2,
        "long": 3
    }

    # If test path is correct...
    if len(test_path) == length[api_type] and test_path.isalnum():
        # Check response status code...
        if response.status_code != 200:
            results["failed"].append({
                "test_path": test_path,
                "status_code": response.status_code,
                "text": response.text
            })
            return

        # ...and response contents
        resp_obj = response.json()
        if len(resp_obj.keys()) == 1 and resp_obj["uid"] and len(resp_obj["uid"]) == 32 and resp_obj["uid"].isalnum():
            results["passed"] += 1
        return
    else:
        # Else, doing otherwise
        if response.status_code != 200:
            results["passed"] += 1
            return
        else:
            results["failed"].append({
                "test_path": test_path,
                "status_code": response.status_code,
                "text": response.text
            })



# Run all tests
print("Running tests...")
for test_path in tests["correct_path"] + tests["incorrect_path"]:
    test_api(test_path, api_type)

# Print final results
print(f'Testing finished! {results["passed"]} / {results["total"]} tests passed!')
if len(results["failed"]):
    for f in results["failed"]:
        print(f'Test "{f["test_path"]}" failed! Status code: {f["status_code"]}. Content: {f["text"]}')

# Exiting with non-zero code if there are failed tests to sign that overall testing failed
if len(results["failed"]):
    sys.exit(2)