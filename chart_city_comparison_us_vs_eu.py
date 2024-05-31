import pollution_eu_vs_us_functions as f


def main():
    us_pollution_dfs_dict, eu_pollution_dfs_dict = f.csv_into_df()

    us_city_avgs, eu_city_avgs = f.calculate_city_avg_pollutions(us_pollution_dfs_dict, eu_pollution_dfs_dict)
    f.create_chart_compare_cities(us_city_avgs, eu_city_avgs)


if __name__ == "__main__":
    main()