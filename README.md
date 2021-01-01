# Data File Reference

### Standard Fields

##### Standard Geographic Field

The following geographic fields are available to represent your data:

* **country_name**
* **region_name**

Along with the above fields, system will automatically derive a **continent** field that may be used in your machine
learning model.

##### Standard Date Fields

The following date fields can be specified in a record:

* **date** - specifies the date for a record. Valid values are in ISO format: YYYY-MM-DD.
* **year** - specifies the year for a record. Valid values are from 0-4000 AD.
* **quarter** - specifies the quarter for a record. Valid values are from 1-4.
* **month**- specifies the month number for a record. Valid values are from 1-12.
* **week** - used to specify the week number for a record. Valid values are from 1-53
* **day_of_year**- used to specify the day of year for the record. Valid values are from 1-365, or 1-366 for leap years.
* **day_of_month** - used to specify the day of month for a record.
* **day_of_week** - used to specify the day of a given week. Valid values are from 1-7, where 1 = Monday and 7 = Sunday

Depending on the type of data you are merging into your dataset, you may use different fields.

##### Examples of modeling dates

a. if you are model in quarterly economic reports, you would only use the **country_name**, **year**, and **quarter**
fields. You would not repeat the same data for every day of a quarter. When the dataset is merged with the other case
data, it will be exploded to a daily basis.

b. if you model average temperatures per quarter each year, you might only specify the **country_name**, **region_name**
, and **quarter** field. Again, you do not specify the same data for every day of every quarter of every year you are
modelling. Just specify the data for each quarter, and it will be exploded when merged to your dataset.

c. if you model population by country each year, you would only use the **country_name** field and **year** field

d. if you model holidays that are on fixed days each year, such as December 25, you would use the **month** and **
day_of_month**
field.

##### Derived Date Fields

In the machine learning model it may be important to input information on a week number, quarter, or day of year.
Regardless of the date fields used to represent your data, all other date fields will be derived and available for input
into your model. For example, if you specify only the **date**
in your, the **week**, **day_of_year**, **quarter**, **month**, etc... are derived and usable.
