import requests
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


def generate_dates(size):
    """
    Generates the list of dates that goes back as dictated by the 'size' parameter.
    """

    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(size)]
    return date_list


def megalotto_parser(date):
    """
    Returns a pandas df row with Lotto winnings on provided date, parsing the results from the
    megalotto.pl website.
    """

    request = requests.get('http://megalotto.pl/wygrane/lotto/'+date)
    file_content = str(request.content)
    db = {}
    participants = 0
    winnings = 0

    before_value = '</td><td class="czarny">'
    after_value = '</td>'
    before = {"6": '<tr><td class="czarny" style="text-align: left;">sz\\xc3\\xb3stka'
            '</td><td class="zielony">',
        "5": '<tr><td class="czarny" style="text-align: left;">pi\\xc4\\x85tka'
            '</td><td class="zielony">',
        "4": '<tr><td class="czarny" style="text-align: left;">czw\\xc3\\xb3rka'
            '</td><td class="zielony">',
        "3": '<tr><td class="czarny" style="text-align: left;">tr\\xc3\\xb3jka'
            '</td><td class="zielony">'}
    no_draw = "Brak losowania w tym dniu"

    if file_content.find(no_draw) < 0:
        for number in before:
            index = file_content.find(before[number]) + len(before[number])
            end = file_content[index:].find(before_value) + index
            howmany = int(file_content[index:end])

            index = end + len(before_value)
            end = file_content[index:].find(after_value) + index
            value = file_content[index:end].replace(" ", "")
            value = float(value) * howmany

            db["no_"+number] = howmany
            db["value_"+number] = value
            participants += howmany
            winnings += value
        db["winning_tickets"] = winning_tickets
        db["winnings"] = winnings

    df = pd.DataFrame(db, index=[date])
    return df


def get_lotteries_data(size):
    """
    Compiles a dataframe with Lotto winnings on dates fitting in a proposed timeframe.
    """

    date_list = generate_dates(size)
    lotteries = pd.Dataframe()
    for date in date_list:
        time.sleep(1)
        date = date.strftime("%d-%m-%Y")
        df = megalotto_parser(date)
        lotteries = lotteries.append(df)
    return lotteries


def predict_winning_tickets(lotteries):
    X = lotteries[lotteries["no_6"] > 0][["value_6"]]
    y = lotteries[lotteries["no_6"] > 0]["winning_tickets"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    model = LinearRegression().fit(X_train, y_train)
    return model


def esperance_pred(lotteries, prize6):
    """
    Calculates the expected value using a modified formula, which predicts the number of all
    tickets, which increases a chance that the main prize is divided between multiple winners.
    """

    prob3 = 1/57
    prize3 = lotteries.value_3.sum()/lotteries.no_3.sum()
    prob4 = 1/1032
    prize4 = lotteries[lotteries["no_6"] == 0].value_4.sum()/lotteries[
        lotteries["no_6"] == 0].no_4.sum()
    # Payout mechanisms of 4, 5 may differ slightly depending on the main prize (6) being won.
    prize4_6 = lotteries[lotteries["no_6"] > 0].value_4.sum()/lotteries[
        lotteries["no_6"] > 0].no_4.sum()
    prob5 = 1/52401
    prize5 = lotteries[lotteries["no_6"] == 0].value_5.sum()/lotteries[
        lotteries["no_6"] == 0].no_5.sum()
    prize5_6 = lotteries[lotteries["no_6"] > 0].value_5.sum()/lotteries[
        lotteries["no_6"] > 0].no_5.sum()
    prob6 = 1/13983816

    model = predict_winning_tickets(lotteries)
    winning_tickets = float(model.predict([[prize6]]))
    all_tickets = winning_tickets / (prob3 + prob4 + prob5 + prob6)
    # We divide situation in two cases: whether the main prize is being won, or not.
    happens_6 = 1 - pow(1 - prob6, all_tickets)
    # Winning '3' is always the same, the other stuff differs.
    esperance = prob3 * prize3 + (1 - happens_6) * (prob4 * prize4 + prob5 * prize5)
    # Term 'prob6' is present in the formula, but it reduces itself.
    esperance = esperance + happens_6 * (prob4 * prize4_6 + prob5 * prize5_6
        + prize6 / all_tickets)
    return esperance


def esperance_usual(lotteries, prize6):
    """
    Calculates the expected value using the standard formula.
    """

    prob3 = 1/57
    prize3 = lotteries.value_3.sum()/lotteries.no_3.sum()
    prob4 = 1/1032
    prize4 = lotteries.value_4.sum()/lotteries.no_4.sum()
    prob5 = 1/52401
    prize5 = lotteries.value_5.sum()/lotteries.no_5.sum()
    prob6 = 1/13983816

    esperance = prob3 * prize3 + prob4 * prize4 + prob5 * prize5 + prob6 * prize6
    return esperance

# lotteries = get_lotteries_data(1000)
# lotteries.to_csv('lotteries.csv')
lotteries = pd.read_csv("D:\pawel\Documents\github\Lotto\lotteries.csv")
# Plotting the expected values calculated with two different methods.
linspace = np.linspace(2000000, 50000000, 1000)
e_pred = []
e_usual = []
for prize6 in linspace:
    e_pred.append(esperance_pred(lotteries, prize6))
    e_usual.append(esperance_usual(lotteries, prize6))
fig = plt.figure(figsize=(20,10))
plt.plot(linspace, e_pred, label="Predictive model")
plt.plot(linspace, e_usual, label="Classic model")
# The line depicting a price of one ticket.
plt.plot([0, 50000000], [3, 3], color="red", linestyle="dashed", linewidth="1")
plt.xlabel("Prize pool [in 10 mln zł]")
plt.ylabel("Expected value of one ticket")
plt.legend()
plt.savefig("expected_values.png")
