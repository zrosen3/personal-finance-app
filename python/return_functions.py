import pandas as pd



# calculate end return of investment
def calculate_return(principal, interest, years, inflation=0, cap_tax_rate=0):
    raw_return = principal * ((1 + interest / 100) / (1 + inflation / 100)) ** years
    taxes = (raw_return - principal) * cap_tax_rate / 100
    tax_adjusted_return = raw_return - taxes
    value_added = tax_adjusted_return - principal
    return [round(tax_adjusted_return, 2), round(taxes, 2), round(value_added, 2)]


# create dataframe of investment over time
def create_df(principal, interest, years, inflation=0, cap_tax_rate=0):
    d = {'Year': [int(year) for year in range(0, int(years) + 1)]}
    df = pd.DataFrame(data=d)
    df["Value"] = 1.0
    df["Value"] = principal * ((1 + interest / 100) / (1 + inflation / 100)) ** df['Year']
    df["Capital gains tax"] = (df["Value"] - principal) * cap_tax_rate / 100
    df["Tax adjusted return"] = df["Value"] - df["Capital gains tax"]
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
    nominal_price_df = df_returns.loc[
        (df_returns['year'] >= purchase_year) & (df_returns['year'] <= sale_year), ["year", annual_df_returns_var]]
    nominal_price_df.loc[nominal_price_df['year'] == purchase_year, 'value_before_year'] = investment_amount
    nominal_price_df.reset_index(inplace=True)
    for i in range(1, len(nominal_price_df)):
        nominal_price_df.loc[i, 'value_before_year'] = nominal_price_df.loc[i - 1, 'value_before_year'] * (
                    1 + nominal_price_df.loc[i - 1, annual_df_returns_var])
    nominal_sale_price = nominal_price_df.loc[nominal_price_df['year'] == sale_year, 'value_before_year']
    nominal_sale_price = float(nominal_sale_price.iloc[0])

    # calculate real sale price
    real_price_df = df_returns.loc[
        (df_returns['year'] >= purchase_year) & (df_returns['year'] <= sale_year), ["year", real_df_returns_var]]
    real_price_df.loc[real_price_df['year'] == purchase_year, 'real_value_before_year'] = investment_amount
    real_price_df.reset_index(inplace=True)
    for i in range(1, len(real_price_df)):
        real_price_df.loc[i, 'real_value_before_year'] = real_price_df.loc[i - 1, 'real_value_before_year'] * (
                    1 + real_price_df.loc[i - 1, real_df_returns_var])
    real_sale_price = real_price_df.loc[real_price_df['year'] == sale_year, 'real_value_before_year']
    real_sale_price = float(real_sale_price.iloc[0])

    # calculate total tax
    tax = (nominal_sale_price - investment_amount) * cap_tax_rate / 100

    # calculate nominal sale price less tax
    nominal_sale_price_tax = float(nominal_sale_price - tax)

    # calculate real value of investment at end of time period
    # divide by (1+ inflation rate) for each year
    inflation_df = df_returns.loc[
        (df_returns['year'] >= purchase_year) & (df_returns['year'] <= sale_year), ["year", "inflation_rate"]]
    inflation_df.loc[inflation_df['year'] == sale_year, 'tax_adjusted_real_value'] = nominal_sale_price_tax
    inflation_df.reset_index(inplace=True)
    for i in range(len(real_price_df) - 2, -1, -1):
        inflation_df.loc[i, 'tax_adjusted_real_value'] = inflation_df.loc[i + 1, 'tax_adjusted_real_value'] / (
                    1 + inflation_df.loc[i, "inflation_rate"])
    real_end_value_tax = inflation_df.loc[real_price_df['year'] == purchase_year, 'tax_adjusted_real_value']
    real_end_value_tax = float(real_end_value_tax.iloc[0])

    # calculate real return
    real_return_tax = real_end_value_tax - investment_amount

    # create dataframe of different financial variables to return
    d = {"Initial investment amount": investment_amount,
         "Nominal sale price": nominal_sale_price,
         "Real sale price": real_sale_price,
         "Tax": tax,
         "Nominal sale price minus tax": nominal_sale_price_tax,
         "Real value of nominal sale price minus tax": real_end_value_tax,
         "Real return including inflation and tax": real_return_tax}
    df_final = pd.DataFrame(d, index=[1])

    # print statement to debug
    # =============================================================================
    #     print("Initial investment:")
    #     print(investment_amount)
    #     print("Nominal sale price: ")
    #     print(nominal_sale_price)
    #     print("Real sale price: ")
    #     print(real_sale_price)
    #     print("Capital gains tax: ")
    #     print(tax)
    #     print("Nominal sale price less tax: ")
    #     print(nominal_sale_price_tax)
    #     print("Real value of nominal sale price less tax: ")
    #     print(real_end_value_tax)
    #     print("Real return including inflation and tax: ")
    #     print(real_return_tax)
    #     print("All return values:")
    #     print(df_final)
    # =============================================================================

    # return list of variables
    return df_final


df_returns = pd.read_excel(r'../data/Output/Returns dataset.xlsx', sheet_name="r.data")
investment_choice = 'S&P 500'
investment_amount = 1000
purchase_year = 1998
sale_year = 2022
cap_tax_rate = 15
# Test these functions a few times
# df = historical_returns(df_returns, 'S&P 500', 1000, 1998, 2020, 15)
# df = historical_returns(df_returns, '3 month treasury bill', 1000, 1998, 2020, 15)
df = historical_returns(df_returns, 'US treasury bond', 1000, 1998, 2022, 15)
# df = historical_returns(df_returns, 'BAA corporate bond', 1000, 1998, 2020, 15)
# df = historical_returns(df_returns, 'Real estate', 1000, 1998, 2020, 15)


# print(calculate_tax_rate(50000, "Single"))
# print(calculate_tax_rate(10000000, "Single"))
# print(calculate_tax_rate(200000, "Married, filing separately"))
# print(calculate_return(100, 10, 10, 1, 1))
# df = create_df(100, 10, 30, 1, 1)
# df2 = create_df(100, 10, 30, 1, 50)
# print(calculate_return(100, 10, 1, 1, 1))
# print(create_df(100, 10, 1, 1, 1))

# print(calculate_return(100, 10.1, 1, 1, 1))
# print(create_df(100, 10, 1, 1, 1))

# print(calculate_return(100, 10, 1, 1, 1))
# print(create_df(100, 10, 1, 1, 1))

# print(calculate_return(100, 10, 1, 1, 1))
# print(create_df(100, 10, 1, 1, 1))
