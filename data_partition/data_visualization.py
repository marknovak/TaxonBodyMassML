import pandas as pd
import matplotlib.pyplot as plt

#separate a dataset into (num_bins) bins and display a histogram based on "mass_g" variable
#Split each bin into its own dataframe and return as a list
#inputs: dataframe with "mass_g" variable containing a float of a species mass
#        num_bins = number of bins to use for histogram
def print_and_calc(name, df, num_bins):
    print(df)
    counts, bin_edges, _ = plt.hist(df["mass_g"], bins=num_bins)
    plt.title(f"{name} original distribution")
    plt.show()
    plt.cla()
    print("Bin counts:", counts)
    print("Bin edges", bin_edges)
    df_bins = []
    for i in range(num_bins):
        bin_mask = (df["mass_g"] > bin_edges[i]) & (df["mass_g"] <= bin_edges[i + 1])
        curr_bin = df[bin_mask]
        df_bins.append(curr_bin)
        print("Bin", i, ": \n", curr_bin)
    return df_bins

#split each bin into test and training data based
def separate_test_train(df_bins, test_train_split_proportion):
    test = pd.DataFrame()
    train = pd.DataFrame()
    for bin in df_bins:
        if len(bin) == 0:
            print("Empty bin")
        else:
            sample = bin.sample(frac=test_train_split_proportion, replace=False)
            bin = bin.drop(sample.index)
            print("Sample:", sample)
            print("Train:", bin)
            test = pd.concat([test, sample])
            train = pd.concat([train, bin])

    return test, train
            
    
    
def main():
    df = pd.read_csv("../data/BodyMass.csv")
    low_bound = 1
    high_bound = 10000
    num_bins = 30
    test_train_split_proportion = 0.1
    low = df[df["mass_g"] < low_bound]
    mid = df[df["mass_g"] < high_bound] 
    mid = mid[mid["mass_g"] >= low_bound] 
    high = df[df["mass_g"] >= high_bound]
    
    low_bins = print_and_calc("low", low, num_bins)
    mid_bins = print_and_calc("mid", mid, num_bins)
    high_bins = print_and_calc("high", high, num_bins)
    
    low_test, low_train = separate_test_train(low_bins, test_train_split_proportion)
    mid_test, mid_train = separate_test_train(mid_bins, test_train_split_proportion)
    high_test, high_train = separate_test_train(high_bins, test_train_split_proportion)
    
    test = pd.concat([low_test, mid_test, high_test])
    train = pd.concat([low_train, mid_train, high_train])
    
    plt.hist(low_test["mass_g"], bins=num_bins)
    plt.title("Low test distribution")
    #I saved pngs of your histograms to display on the website -Hailey
    plt.savefig("../web_dev/low_test.png")
    plt.show()
    plt.cla()
    
    plt.hist(mid_test["mass_g"], bins=num_bins)
    plt.title("Mid test distribution")
    plt.savefig("../web_dev/mid_test.png")
    plt.show()
    plt.cla()
    
    plt.hist(high_test["mass_g"], bins=num_bins)
    plt.title("High test distribution")
    plt.savefig("../web_dev/high_test.png")
    plt.show()
    plt.cla()
    
    test.to_csv("test.csv", index=False)
    train.to_csv("train.csv", index=False)

main()
