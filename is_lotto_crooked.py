import pandas as pd
import random


def chi_test(results, columns):
    """
    The chi-squared test statistic is the sum of (OBSERVED - EXPECTED)^2 / EXPECTED over the set of
    observations. It's performed independently for each number in 1-49.
    """

    howmany = []
    for i in range(1,50):
        occurences = 0
        for column in columns:
            occurences += len(results[results[column] == i])
        howmany.append(occurences)
    chisquared = 0
    # The probability of the specific number being chosen is 1 - 43/49 = 6/49.
    expected = 6/49 * len(results)
    for occurences in howmany:
        statistic = occurences - expected
        statistic = statistic*statistic/expected
        chisquared += statistic
    return chisquared


def iterate_chi_test(results, resolution=5, no_draws=100, start_at=0):
    """
    Iterates the chi_test function over the whole set, selecting the subsets of the size no_draws
    and moving ahead according to the function's resolution.  Returns the number of times the
    test's p-value was sufficiently small, and the greatest value of the test statistic.
    """

    i = start_at
    count = 0
    max = 0
    while i < (len(results)-no_draws):
        subset = results[i:(i+no_draws)]
        result = chi_test(subset, columns)
        # For 48 degrees of freedom, 58.1 corresponds to p-value of ~0.15 for the test statistic.
        if result > 58.1:
            if result > max:
                max = result
            count += 1
        i += resolution
    return count, max


def generate_fake_results(size):
    """
    Generates fake lotto results of specified size, with the help of random.choice function.  Does
    not sort the draws, since it's irrelevant to the probability.
    """

    fake_results = pd.DataFrame()
    set = []
    for i in range(1, 50):
        set.append(i)
    for i in range(size):
        df = {}
        new_set = set.copy()
        for column in columns:
            df[column] = random.choice(new_set)
            new_set.remove(df[column])
        df = pd.DataFrame(df, index=[i])
        fake_results = fake_results.append(df)
    return fake_results


filename = "dl.csv"
results = pd.read_csv(filename, names=["no", "date", "1st", "2nd", "3rd", "4th", "5th", "6th"])
results.drop(["no"], axis=1, inplace=True)

fake_results = generate_fake_results(len(results))
iterate_chi_test(results)
iterate_chi_test(fake_results)
# Well, it's probably not.
