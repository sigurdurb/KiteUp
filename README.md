# KiteUp

Script in a Jupyter Notebook that queries Icelandic weather stations for kite–able locations.

When all info is correct this could be set up as an email alert service.

## Setup
* python3
* pip install -r requirements.txt



## About: API
API documentation : [apis.is](http://docs.apis.is/#endpoint-weather), [github](https://github.com/apis-is/apis/blob/master/endpoints/weather/documentation.md)

The forecasts that are queried are generally given out 

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