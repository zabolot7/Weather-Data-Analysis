import pollution_us_vs_eu_functions as f


def main():
    us_pollution_dfs_dict, eu_pollution_dfs_dict = f.csv_into_df()
    us_medians, eu_medians = f.calculate_continent_median_pollutions(us_pollution_dfs_dict, eu_pollution_dfs_dict)
    f.create_bar_chart(us_medians, eu_medians, type="median")


if __name__ == "__main__":
    main()