## Fighter - Flights scraping

Figher is a web scraping tool to get the flights information from google flights from today to next 15 days for the defined roots. You can update the route details in script and make it work.

To install the application follow the below steps:

## Installation

### Prerequisites

Run the following commands to create virtual environment and install the dependencies from your project cloned location

```
python3 -m venv env
```

```
source env/bin/activate
```

```
pip install -r requirements.txt
```

## Getting Started

Go to scrapy.py update the routes list with origin and destination codes for which you need the information.

If you want to scrap data other than fifteen days, you can change the number of days required in the "get_html_obj" function

Finally, run script with your virtual environment activated with the below command

```
python3 scrapy.py
```

After script is executed you can find the results in results directory
