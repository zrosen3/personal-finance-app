import pandas as pd


# calculate end return of investment
def calculate_return(principal, interest, years, inflation=0, cap_tax_rate=0):
    # calculate nominal investment value
    nominal_value = (principal * ((1 + interest / 100)) ** years)
    nominal_return = nominal_value - principal

    # Adjust for taxes
    taxes = max(nominal_return, 0) * cap_tax_rate / 100
    nominal_taxed_value = nominal_value - taxes

    # Adjust for inflation
    real_taxed_value = nominal_taxed_value / ((1 + inflation / 100) ** years)
    real_taxed_return = real_taxed_value - principal
    real_value = nominal_value / (((1 + inflation / 100)) ** years)

    # Return values in labeled single row dataframe
    df = {"Nominal value": round(nominal_value, 2),
          "Nominal return": round(nominal_return, 2),
          "Taxes": round(taxes, 2),
          "Nominal taxed value": round(nominal_taxed_value, 2),
          "Real value": round(real_value, 2),
          "Real taxed value": round(real_taxed_value, 2),
          "Real taxed return": round(real_taxed_return, 2)}
    return df


# create dataframe of investment over time
def create_df(principal, interest, years, inflation=0, cap_tax_rate=0):
    d = {'Year': [int(year) for year in range(0, int(years) + 1)]}
    df = pd.DataFrame(data=d)
    df["Nominal value"] = principal * ((1 + (interest / 100)) ** df["Year"])
    df["Capital gains tax"] = (df["Nominal value"] - principal) * cap_tax_rate / 100
    df["Nominal taxed value"] = df["Nominal value"] - df["Capital gains tax"]
    df["Real value"] = df["Nominal value"] / ((1 + (inflation / 100)) ** df["Year"])
    df["Tax adjusted real value"] = df["Nominal taxed value"] / ((1 + (inflation / 100)) ** df["Year"])
    df["Value"] = df["Tax adjusted real value"]
    return df


# Calculate 2022 capital gains tax rate given income, status, and holding_time
def calculate_tax_rate(income, status):
    tax_rate = 0
    if status == "single":
        if income >= 41676 and income <= 459750:
            tax_rate = 15
        elif income >= 459751:
            tax_rate = 20
    elif status == "married, filing jointly":
        if income >= 83351 and income <= 517200:
            tax_rate = 15
        elif income > 517201:
            tax_rate = 20
    elif status == "married, filing separately":
        if income >= 55801 and income <= 488500:
            tax_rate = 15
        elif income >= 488501:
            tax_rate = 20
    elif status == "head of household":
        if income >= 55801 and income <= 488500:
            tax_rate = 15
        elif income >= 488501:
            tax_rate = 20
    return tax_rate


# Calculate return on investment choice over time given investment choice, amount, purchase date, withdrawal date,
# and capital gains tax
def historical_returns(df_returns, investment_choice, investment_amount, purchase_year, sale_year, cap_tax_rate):
    # extract names of relevant variables from data frames
    var_names = {"S&P 500": "s_p_500_includes_dividends", "3 month treasury bill": "3_month_tbill",
                 "US treasury bond": "us_t_bond",
                 "BAA corporate bond": "baa_corporate_bond", "Real estate": "real_estate"}
    annual_df_returns_var = "annual_returns_" + var_names[investment_choice]
    real_df_returns_var = "annual_real_returns_" + var_names[investment_choice]
    # calculate nominal sale price
    price_df = df_returns.loc[
        (df_returns['year'] >= purchase_year) & (df_returns['year'] <= sale_year), ["year", "inflation_rate",
                                                                                    annual_df_returns_var,
                                                                                    real_df_returns_var]]
    price_df.loc[price_df['year'] == purchase_year, 'value_before_year'] = investment_amount
    price_df.loc[price_df['year'] == purchase_year, 'real_value_before_year'] = investment_amount
    price_df.loc[price_df['year'] == purchase_year, 'tax_adjusted_nominal_value'] = investment_amount
    price_df.loc[price_df['year'] == purchase_year, 'tax_adjusted_real_value'] = investment_amount
    price_df.loc[price_df['year'] == purchase_year, 'tax'] = 0

    price_df.reset_index(inplace=True)
    for i in range(1, len(price_df)):
        price_df.loc[i, 'value_before_year'] = price_df.loc[i - 1, 'value_before_year'] * (
                1 + price_df.loc[i - 1, annual_df_returns_var])
        price_df.loc[i, 'tax'] = max(price_df.loc[i, 'value_before_year'] - price_df.loc[0, 'value_before_year'],
                                     0) * cap_tax_rate / 100
        price_df.loc[i, 'real_value_before_year'] = price_df.loc[i - 1, 'real_value_before_year'] * (
                1 + price_df.loc[i - 1, real_df_returns_var])
        price_df.loc[i, 'tax_adjusted_nominal_value'] = price_df.loc[i, 'value_before_year'] - price_df.loc[
            i, 'tax']
        total_inflation = 1
        for j in range(0, i):
            total_inflation = (1 + price_df.loc[j, 'inflation_rate'])* total_inflation
        price_df.loc[i, 'tax_adjusted_real_value'] = price_df.loc[i, 'tax_adjusted_nominal_value'] /total_inflation
    price_df.reset_index(inplace=True)

    # Return dataframe with value of investment over time
    cols_to_keep = ["year", "value_before_year", "real_value_before_year", "tax", "tax_adjusted_nominal_value", "tax_adjusted_real_value", "inflation_rate",
                           annual_df_returns_var, real_df_returns_var]
    returns_df = price_df[cols_to_keep]
    return returns_df


df_returns = pd.read_excel(r'../data/Output/Returns dataset.xlsx', sheet_name="r.data")
investment_choice = 'S&P 500'
investment_amount = 1000
purchase_year = 1998
sale_year = 2022
cap_tax_rate = 15
# Test these functions a few times
df = historical_returns(df_returns, 'S&P 500', 1000, 1998, 2022, 15)
# df = historical_returns(df_returns, '3 month treasury bill', 1000, 1998, 2020, 15)
# df = historical_returns(df_returns, 'US treasury bond', 1000, 1998, 2022, 15)
# df = historical_returns(df_returns, 'BAA corporate bond', 1000, 1998, 2020, 15)
# df = historical_returns(df_returns, 'Real estate', 1000, 1998, 2020, 15)


# print(calculate_tax_rate(50000, "Single"))
# print(calculate_tax_rate(10000000, "Single"))
# print(calculate_tax_rate(200000, "Married, filing separately"))
# df =calculate_return(principal = 100, interest = 10, years = 10, inflation =1, cap_tax_rate = 1)
# print(calculate_return(principal = 100, interest = 10, years = 10, inflation =1, cap_tax_rate = 1))


#df = create_df(principal=100, interest=10, years=30, inflation=1, cap_tax_rate=1)
#df2 = calculate_return(principal = 100, interest = 10, years = 30, inflation = 1, cap_tax_rate = 1)

# df2 = create_df(100, 10, 30, 1, 50)
# print(calculate_return(100, 10, 1, 1, 1))
# print(create_df(100, 10, 1, 1, 1))

# df_test = calculate_return(principal = 100, interest = 10.1, years = 1, inflation = 1, cap_tax_rate = 1)
# print(df_test)
# print(create_df(100, 10, 1, 1, 1))

# print(calculate_return(100, 10, 1, 1, 1))
# print(create_df(100, 10, 1, 1, 1))

# print(calculate_return(100, 10, 1, 1, 1))
# print(create_df(100, 10, 1, 1, 1))
