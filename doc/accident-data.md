# Origin of the data

There are several sources of data available on the web.

## ANENA

Data are gathered from the [ANENA survey](https://www.anena.org/5041-bilan-des-accidents.htm)
(Association Nationale pour l’Étude de la Neige et des Avalanches) which register snow avalanche
accidents on the French territory from official authorities, usually these accidents triggered a
rescue operation and forensic report.

## SERAC

[SERAC](https://www.camptocamp.org/serac) is an accident database managed by the C2C association.

* [SERAC reports](https://www.camptocamp.org/xreports)
* [Notes on SERAC](https://www.camptocamp.org/articles/697210/fr/base-serac-de-recits-d-incidents-et-accidents)
* [Licenses](https://www.camptocamp.org/articles/106728/fr/licences-des-contenus)

**How to use the API**
```
# List reports
curl 'https://api.camptocamp.org/xreports?xtyp=avalanche,person_fall'

# Get a report
curl 'https://api.camptocamp.org/xreports/1297873?cook=fr'
```

## data-avalanche.org

http://www.data-avalanche.org is a snow avalanche database managed by the relevant association.

* This website is related to [Alain DUCLOS](http://duclos.transmontagne.pagesperso-orange.fr).
* Legally, these data should be considered the proprietary of the association.
* Technically, this website doesn't implement an API.

# Research Analyses

## Fondation Petzl

**Reports**
* [Fondation Patzl — Mieux connaître l’accidentologie des sports de montagne](https://www.petzl.com/fondation/s/accidentologie-des-sports-de-montagne?language=fr)

* for the period 2018-2021
  * [rocher montagne et terrain d'aventure](https://petzl.my.salesforce.com/sfc/p/20000000HrHq/a/68000000D8tZ/aJtbKCJ1So3iXqhPvOrVJS.yFOvpdAfhdHJKaRnm65k)
  * [alpinisme en neige, glace, mixte et cascade de glace](https://petzl.my.salesforce.com/sfc/p/20000000HrHq/a/68000000DBFh/sZHZ7SHgqcOZS4WVTXk_Q8BwTYEmCzsRrkg.H3hEB0U)
  * [ski de randonnée](https://petzl.my.salesforce.com/sfc/p/20000000HrHq/a/68000000DQgE/sK0fpZujo5SOgvo4JDcjcdoTSLc0SR1jtAgIm6KFmGE)
* [2017 : Incidents et quasi-accidents, premiers enseignements et perspectives de prévention](https://petzl.my.salesforce.com/sfc/p/#20000000HrHq/a/68000000D8tj/.trH2IeeEln95olag7tck66umXZduJRvGysPtUKcbHo)
* 2014 : État des lieux et diagnostic

**Researchers**
* [Maud Vanpoulle](http://l-vis.univ-lyon1.fr/staff/maud-vanpoulle) /
  [Laboratoire sur les Vulnérabilités et l’Innovation dans le Sport (L-VIS, Université de Lyon 1)](http://l-vis.univ-lyon1.fr)

# Data Analysis

## Bias on these data

Since we only have high quality data from judicial reports, data cover only accidents that required
a rescue operation.  Thus, we have a lack of data on snow avalanches that didn't have serious
consequences.

Another bias of interpretation on the data is due to the fact we don't have data on the frequencies
of the activities.  We don't have data when and where people practice their activities.  In
principle, we should correct data for such biases when we want to evaluate a risk.  For example, the
frequency of the avalanches in function of the slope orientation could be biased by a non-uniform
frequency of presence.
