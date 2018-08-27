# KiteUp

Jupyter Notebook that queries Icelandic weather stations for kite–able locations.

When all info is correct this could be set up as an email alert service.

## Setup
* python3
* pip install -r requirements.txt



## About: API
The KiteUp program queries the /weather/forecasts endpoint of apis.is, [that code ](https://github.com/apis-is/apis/blob/master/endpoints/weather/index.js) queries various endpoints of vedur.is 

Apis.is API documentation endpoint: [apis.is](http://docs.apis.is/#endpoint-weather), [github](https://github.com/apis-is/apis/blob/master/endpoints/weather/documentation.md)

Time is UTC/GMT.

### vedur.is /forecasts timing
The forecasts that are queried are generally given out at 06:00, 12:00 and 18:00 
### vedur.is /forecasts publishing
According to support(at)vedur.is the forecast are generally published approx 3 and a half hours after they are made.

So a forecast that is made at 12:00 will not be published to the web/API until 15:30 (+- 5 minutes). 

KiteUp follows this publishing plan of [vedur.is](http://vedur.is):

* Forecast made at 06:00 is published at 09:30 
* Forecast made at 18:00 is published in at 21:30
* Forecast made at 12:00 is published at 15:30

KiteUp will query about 10 minutes later then the publishing time, given the +-5 minutes delay that can happen.

According to support forecast updates are written into their database at the same time across all stations when all calculations are finished.

## About: Weather directions

* **N**: Norðan - um vind úr norðurátt.

* **NA**: Norðaustan - um vind úr norðausturátt.
* **NNA**: Norðnorðaustan- um vind úr norðnorðausturátt (mitt á milli norðan og norðaustan).
* **NNV**: Norðnorðvestan - um vind úr norðnorðvesturátt (mitt á milli norðan og norðvestan).
* **NV**: Norðvestan - um vind úr norðvesturátt.

* **S**: Sunnan - um vind úr suðurátt.
* **SSA**: Suðsuðaustan - um vind úr suðsuðausturátt (mitt á milli sunnan og suðaustan).
* **SSV**: Suðsuðvestan - um vind úr suðsuðvesturátt (mitt á milli sunnan og suðvestan).
* **SV**: Suðvestan - um vind úr suðvesturátt.
* **SA**: Suðaustan - um vind úr suðausturátt.

* **V**: Vestan - um vind úr vesturátt.
* **VNV**: Vestnorðvestur - um vind úr vestnorðvesturátt (mitt á milli vestan og norðvestan).
* **VSV**: Vestsuðvestan - um vind úr vestsuðvesturátt (mitt á milli vestan og suðvestan).
* **A**: Austan - um vind úr austurátt.
* **ANA**: Austnorðaustan - um vindátt sem er mitt á milli austan og norðaustan.
* **ASA**: Austsuðaustan - um vindátt sem er mitt á milli austan og suðaustan.


Heimild: [http://www.vedur.is/vedur/frodleikur/greinar/nr/936](http://www.vedur.is/vedur/frodleikur/greinar/nr/936)