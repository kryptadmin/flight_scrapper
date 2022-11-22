import os
import time
import json
import pandas as pd
from random import randint
from datetime import date as _dt, timedelta as _td, time as _t
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from requests_html import HTML

# List of routes
routes = [
        ["ORD", "DCA"],
        ["ORD", "MCO"],
        ["ATL", "JFK"],
        ["ATL", "ORD"],
        ["ORD", "JFK"],
        ["ORD", "LAX"],
        ["LAX", "JFK"],
        ["JFK", "LHR"],
        ["LAX", "ICN"],
        ["LHR", "ICN"],
]

# Base url
url = "https://www.google.com/travel/flights?q=Flights%20to%20{}%20from%20{}%20on%20{}%20through%20{}"


def get_driver():
    # Chrome browser options
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    return driver

def get_html_obj():
    dt_range = [str(_dt.today() + _td(n+1)) for n in range(15)]
    for route in routes:
        for dt in dt_range:
            driver = get_driver()
            base = url.format(route[0], route[1], dt, dt)
            driver.get(base)
            time.sleep(randint(60, 90))
            
            try:
                load_more = "//div[@class='zISZ5c QB2Jof']"
                load_element = driver.find_element(by=By.XPATH, value=load_more)
                if load_element:
                    load_element.click()
                    time.sleep(randint(25,35))
            except Exception as e:
                pass

            expand_elements = "//div[@class='vJccne  trZjtf']"
            eles = driver.find_elements(by=By.XPATH, value=expand_elements)

            for element in eles:
                try:
                    element.click()
                    time.sleep(1)
                except Exception as e:
                    pass
            
            flight_elements = "//div[@class='gQ6yfe W6QfXd']"
            elements = driver.find_elements(by=By.XPATH, value=flight_elements)
            rows = []
            for ele in elements:
                try:
                    html_obj = HTML(html=ele.get_attribute("innerHTML"))
                    row = {
                        "price": "Price Unavailable", 
                        "stops": "Non Stop", 
                        "trip_type": "roundtrip",
                        "origin": route[0],
                        "destination": route[1], 
                        "journey_date": dt, 
                        "return_date": dt,
                    }
                    price = "Price Unavailable"
                    price1 = html_obj.find("div.YMlIz.FpEdX")
                    price2 = html_obj.find("div.YMlIz.FpEdX.jLMuyc")
                    if price1 and len(price1) > 0:
                        price = price1[0].find("span")[0].text
                    elif price2 and len(price2) > 0:
                        price = price2[0].find("span")[0].text

                    row["price"] = price
                    layovers = html_obj.find("div.tvtJdb.eoY5cb.y52p7d")
                    stop1 = html_obj.find("div.c257Jb.QwxBBf.eWArhb")
                    if stop1:
                        row["stops"] = "Non Stop"
                        spans = stop1[0].find("span")
                        airbus_spans = [span.text for span in stop1[0].find("span.Xsgmwe")]
                        dep_span = [span for span in spans if "aria-label" in span.attrs and "Departure time:" in span.attrs["aria-label"]]
                        arr_span = [span for span in spans if "aria-label" in span.attrs and "Arrival time:" in span.attrs["aria-label"]]
                        row["stop1_origin"] = stop1[0].find("div.dPzsIb.AdWm1c.y52p7d")[0].text
                        row["stop1_destination"] = stop1[0].find("div.SWFQlc.AdWm1c.y52p7d")[0].text
                        if len(dep_span):
                            row["stop1_dep_time"] = dep_span[0].text
                        if len(arr_span):
                            row["stop1_arr_time"] = arr_span[0].text

                        row["stop1_airlines"] = airbus_spans[0]
                        row["stop1_airbus"] = airbus_spans[3]
                        row["stop1_airbus_no"] = airbus_spans[4]
                        row["stop1_traveltime"] = stop1[0].find("div.CQYfx.y52p7d")[0].text

                    stops = html_obj.find("div.c257Jb.eWArhb")
                    stops = [stop for stop in stops if "QwxBBf" not in stop.attrs["class"]]
                    if stops:
                        row["stops"] = "{} Stops".format(len(stops))
                        i = 2
                        for stop in stops:
                            airbus_spans = [span.text for span in stop.find("span.Xsgmwe")]
                            row["stop{}_origin".format(i)] = stop.find("div.dPzsIb.AdWm1c.y52p7d")[0].text
                            row["stop{}_destination".format(i)] = stop.find("div.SWFQlc.AdWm1c.y52p7d")[0].text
                            spans = stop.find("span")
                            dep_span = [span for span in spans if "aria-label" in span.attrs and "Departure time:" in span.attrs["aria-label"]]
                            arr_span = [span for span in spans if "aria-label" in span.attrs and "Arrival time:" in span.attrs["aria-label"]]
                            if len(dep_span):
                                row["stop{}_dep_time".format(i)] = dep_span[0].text
                            if len(arr_span):
                                row["stop{}_arr_time".format(i)] = arr_span[0].text

                            row["stop{}_airlines".format(i)] = airbus_spans[0]
                            row["stop{}_airbus".format(i)] = airbus_spans[3]
                            row["stop{}_airbus_no".format(i)] = airbus_spans[4]
                            row["stop{}_traveltime".format(i)] = stop1[0].find("div.CQYfx.y52p7d")[0].text
                            i = i + 1

                    i = 0
                    for layover in layovers:
                        row["layover{}"] = layover.text
                        i = i + 1

                    rows.append(row)
                except Exception as e:
                    print("Exception for parsing **** {}".format(str(e)))
                    pass
                
            filename = "./results/{}-{}-{}-{}.csv".format(route[0], route[1], "".join(dt.split("/")), str(int(time.time())))
            if not os.path.exists(filename) and len(rows) > 0:
                df = pd.read_json(json.dumps(rows))
                df.to_csv(filename)
            driver.quit()
            print("Scraping completed for {} {} for {} through {}".format(route[0], route[1], dt, dt))
            # time.sleep(10)

if __name__ == "__main__":
    get_html_obj()
