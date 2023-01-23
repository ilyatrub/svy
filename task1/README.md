## Testing API

The strategy is make requests to API endpoint and check that we get correct responses for correct requests.

Request: 2 or 3 alphanumeric symbols (depending on `short` or `long` API type)
Response: status code 200 and JSON object with `uid` key, which has 32-symbol long and alphanumeric value

Any other request should lead to non-200 status code and unpredicted contents in response.

To test API endpoind we need to provide a set of correct and incorrect requests.
The correct request is described above. To reflect all edge cases, we should consider:
- only lowercase letters
- only uppercase letters
- only digits
- same letters or digits
- combinations of lower- and uppercase letters and digits

Incorrect request is either has incorrect length (shorter or longer), or has non-alphanumeric chars in it.
I tried to reflect it in test cases in `tester.py`

## Docker

To build image: `docker build -t <your_tag> .`
To run image:
```
docker run --name <name> \
    -e TEST_URL=<some_url> \
    -e API_TYPE=[short|long] \
    <image_tag>
```
Providing TEST_URL and API_TYPE is optional, they have defaults (`https://ionaapp.com/assignment-magic/dk/` and `short`)

## Additional thoughts

- Test cases can be enhanced by generating them. But this will lead to 62^2 or 62^3 of only correct requests
and bigger at least by the order of magnitude amount of test cases for incorrect requests. Running such a large
amount of test cases definetely will take more time
- We can use parallel computation to speed up the process
- URL and API type can be passed as command line arguments, if it is needed
- Making HTTP request and getting JSON contents of response can be wrapped with exception handlers
- Additional useful output can be added