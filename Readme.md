### Lotto analysis

The set of two Python scripts and associated files:

- *lotto.py* contains both functions for parsing the Lotto results/winnings from a website, and for calculation ofthe  expected value of taking part in a classic Lotto lottery, as a function of prize pool. In a simple predictive model, the prize pool also increases the amount of players, therefore lowering the expected value.
	- *lotteries.csv* contains records of winnings spanning from February 2018 to November 2020;
	- *expected_values.png* compares both "classic" and "predictive" models of expected value with the prize of a lottery ticket.

- *is_lotto_crooked.py* debunks a hypothesis that numbers getting drawn suspiciously often in a short timespans are anything more than a coincidence, by comparing the real and fake Lotto draws with chi-squared test.
	- *dl.csv* contains over 5000 Lotto draws (I think I've just downloaded it from somewhere).