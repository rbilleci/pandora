# Date Preparation Pipeline

First, the geo file is loaded which is a list of countries and regions. The dataset is expanded to the time range.

Additional data modules are loaded, with each data module going through the following steps:

1. file loaded
2. filter
3. time expansion
4. date/time fields added
4. missing values marked
5. missing values imputed
6. filtered to time range
7. validated
8. merged

Any data that is derived from multiple datasets must be performed in the ML Pipeline. This isolates data modules and
allows for derived features to take advantage of hyper-parameter searching. For example, if we have a derived feature
that is a moving average of another feature, the time period of the moving average can be defined as a hyper-parameter,
and the optimal value will be searched for during training.

# ML Pipeline

...

# Data Module Reference

Each Data Module includes the following:

1. a Python file containing constants for each field, location of the dataset, and standard code for missing value
   imputation
2. a file containing the actual dataset; in any format supported by [Pandas](https://pandas.pydata.org/)
3. an __optional__ Python file that can update its dataset, for example, by downloading the latest data from the
   internet or performing some preprocessing that might change over time. The system does __not__ execute the update
   script automatically.

### Standard Data Module Fields

##### Standard Geo Fields

Every data module may designate one or more fields that indicate the data records are related to a country and or
region. If none of the fields below are specified, the data is assumed to apply to all countries and regions.

The field names to use are:

* **For the country:** use one of `country_code`, `country_code3`, or
  `country_code_numeric` - the code fields use the ISO-3166 two-letter, three-letter, and numeric codes. 
  You may identify the country with `country_name`, but it is not preferred since a difference in more difficult to match
* **For the state or province:** use `region_name`

A single data file may have records both at a country level and at a regional level, for example:

| country_code | region_name | population | 
| --- | --- | --- |
| DE |  | 83,000,000 |
| DE | Bavaria | 13,000,000 |
| DE | Berlin | 3,650,000 |
| IT |  | 60,000,000 |

##### Standard Date/Time Fields

The following date fields can be specified in a record:

* **date** - specifies the date for a record. Valid values are in ISO format: YYYY-MM-DD.
* **year** - specifies the year for a record. Valid values are from 0-4000 AD.
* **quarter** - specifies the quarter for a record. Valid values are from 1-4.
* **month**- specifies the month number for a record. Valid values are from 1-12.
* **week** - used to specify the week number for a record. Valid values are from 1-53
* **day_of_year**- used to specify the day of year for the record. Valid values are from 1-365, or 1-366 for leap years.
* **day_of_month** - used to specify the day of month for a record.
* **day_of_week** - used to specify the day of a given week. Valid values are from 1-7, where 1 = Monday and 7 = Sunday

When the data module is loaded, the records are expanded to fill at least the time range used for training, then
enhanced with all date/time fields listed above. This enables missing value imputation based on trends related to a day
of year, week, month, or quarter.

##### Examples of modeling dates

a. if you are model in quarterly economic reports, you would only use the **country**, **year**, and **quarter**
fields. You would not repeat the same data for every day of a quarter. When the dataset is merged with the other case
data, it will be exploded to a daily basis.

b. if you model average temperatures per quarter each year, you might only specify the **country**, **region**
, and **quarter** field. Again, you do not specify the same data for every day of every quarter of every year you are
modelling. Just specify the data for each quarter, and it will be exploded when merged to your dataset.

c. if you model population by country each year, you would only use the **country** field and **year** field

d. if you model holidays that are on fixed days each year, such as December 25, you would use the **month** and **
day_of_month**
field.

##### Derived Date Fields

In the machine learning model it may be important to input information on a week number, quarter, or day of year.
Regardless of the date fields used to represent your data, all other date fields will be derived and available for input
into your model. For example, if you specify only the **date**
in your, the **week**, **day_of_year**, **quarter**, **month**, etc... are derived and usable.
