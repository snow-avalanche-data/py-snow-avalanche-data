# Description

This repository contains French snow avalanche accident data stored in
[JSON](https://www.json.org/json-en.html) and analysis tools written in
[Python](https://www.python.org) language.

# Origin of the data

Data are gathered from the [ANENA survey](https://www.anena.org/5041-bilan-des-accidents.htm)
(Association Nationale pour l’Étude de la Neige et des Avalanches) which register snow avalanche
accidents on the French territory from official authorities, usually these accidents triggered a
rescue operation and judicial report.

There are other data sources available on the web.

## SERAC

[SERAC](https://www.camptocamp.org/serac) is an accident database managed by the C2C association.

* https://www.camptocamp.org/articles/697210/fr/base-serac-de-recits-d-incidents-et-accidents
* https://www.camptocamp.org/articles/106728/fr/licences-des-contenus

## data-avalanche.org

http://www.data-avalanche.org is a snow avalanche database managed by the relevant association.

* This website is related to [Alain DUCLOS](http://duclos.transmontagne.pagesperso-orange.fr).
* Legally, these data should be considered the proprietary of the association.
* Technically, this website doesn't implement an API.

# Bias on these data

Since we only have high quality data from judicial reports, data cover only accidents that required
a rescue operation.  Thus, we have a lack of data on snow avalanches that didn't have serious
consequences.

Another bias of interpretation on the data is due to the fact we don't have data on the frequencies
of the activities.  We don't have data when and where people practice their activities.  In
principle, we should correct data for such biases when we want to evaluate a risk.  For example, the
frequency of the avalanches in function of the slope orientation could be biased by a non-uniform
frequency of presence.

# About Authors

* Fabrice SALVAIRE holds a PhD in data analysis in high energy physics, works as computer scientist,
  and perform climbing, mountaineering and ski touring during his free time (affiliated with the
  sports federation [FSGT/ROC14](https://www.fsgt.org/activites/escal_mont)).