import pollution_us_vs_eu_functions as f


def main():
    us_pollution_dfs_dict, eu_pollution_dfs_dict = f.csv_into_df()
    us_avgs, eu_avgs = f.calculate_continent_avg_pollutions(us_pollution_dfs_dict, eu_pollution_dfs_dict)
    f.create_bar_chart(us_avgs, eu_avgs, type="average")


if __name__ == "__main__":
    main()