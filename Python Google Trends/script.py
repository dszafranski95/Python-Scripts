from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt

# Initialize pytrends
pytrends = TrendReq(hl="en-US", tz=360)


# Function to fetch and display the top trending topics for a given country
def get_top_trending_topics(country_code):
    try:
        trending_searches_df = pytrends.trending_searches(pn=country_code)
        trending_searches_df.columns = ["Trending Topics"]
        print(f"\nTop trending topics in {country_code.upper()}:")
        print(trending_searches_df.head(10).to_string(index=False))
        trending_searches_df.to_csv(f"{country_code}_trending.csv", index=False)
    except Exception as e:
        print(f"Unable to fetch top trending topics for '{country_code}': {str(e)}")


# Function to fetch interest by region for a keyword
def get_interest_by_region(keyword):
    try:
        pytrends.build_payload([keyword], cat=0, timeframe="now 1-d", geo="", gprop="")
        interest_by_region_df = pytrends.interest_by_region()
        if keyword not in interest_by_region_df.columns:
            print(f"No regional data available for '{keyword}'")
            return
        interest_by_region_df = interest_by_region_df[
            interest_by_region_df[keyword] > 0
        ]
        interest_by_region_df = interest_by_region_df.sort_values(
            by=keyword, ascending=False
        )
        print(f"\nInterest in '{keyword}' by region:")
        print(interest_by_region_df.head(10).to_string())
        interest_by_region_df.to_excel(f"{keyword}_interest_by_region.xlsx")
    except Exception as e:
        print(f"Unable to fetch interest by region for '{keyword}': {str(e)}")


# Function to fetch related queries for a keyword
def get_related_queries(keyword):
    try:
        pytrends.build_payload([keyword], cat=0, timeframe="now 1-d", geo="", gprop="")
        related_queries = pytrends.related_queries()

        # Check if data is available
        if related_queries and keyword in related_queries:
            # Check if 'top' list is not empty
            if (
                related_queries[keyword].get("top") is not None
                and not related_queries[keyword]["top"].empty
            ):
                print(f"\nRelated queries for '{keyword}':")
                print(related_queries[keyword]["top"].head(10).to_string(index=False))
            else:
                print(f"\nNo related queries available for '{keyword}'")
        else:
            print(f"\nNo data available for '{keyword}'")
    except IndexError:
        print(f"\nUnable to fetch related queries for '{keyword}' - no data available.")
    except Exception as e:
        print(f"\nUnexpected error for '{keyword}': {str(e)}")


# Function to fetch trends by category for a keyword
def get_trends_by_category(keyword, category):
    try:
        pytrends.build_payload(
            [keyword], cat=category, timeframe="now 1-d", geo="", gprop=""
        )
        data = pytrends.related_topics()

        if data and keyword in data:
            # Iterate through all available topic types (e.g., 'top', 'rising')
            for topic_type, df in data[keyword].items():
                if df is not None and not df.empty:
                    print(
                        f"\nTop topics in category '{category}' for '{keyword}' ({topic_type}):"
                    )
                    print(df.head(10).to_string(index=False))
                else:
                    print(
                        f"\nNo data for category '{category}' and type '{topic_type}' for '{keyword}'"
                    )
        else:
            print(f"\nNo data for category '{category}' and keyword '{keyword}'")
    except IndexError:
        print(
            f"\nUnable to fetch trends by category for '{keyword}' - no data available."
        )
    except Exception as e:
        print(f"\nUnexpected error for '{keyword}' in category {category}: {str(e)}")


# Function to fetch interest over time for a keyword
def get_interest_over_time(keyword, timeframe="today 12-m"):
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=timeframe, geo="", gprop="")
        interest_over_time_df = pytrends.interest_over_time()

        if not interest_over_time_df.empty:
            print(f"\nInterest in '{keyword}' over time:")
            print(interest_over_time_df.head(10).to_string())
            interest_over_time_df.to_excel(f"{keyword}_interest_over_time.xlsx")
        else:
            print(f"\nNo data for '{keyword}' during the selected period")
    except Exception as e:
        print(f"\nUnable to fetch interest over time for '{keyword}': {str(e)}")


# Function to save data in different formats
def save_to_file(dataframe, filename, file_format="csv"):
    try:
        if file_format == "csv":
            dataframe.to_csv(f"{filename}.csv", index=False)
        elif file_format == "excel":
            dataframe.to_excel(f"{filename}.xlsx", index=False)
    except Exception as e:
        print(f"\nUnable to save file '{filename}' in format '{file_format}': {str(e)}")


# Function to visualize interest over time with pagination
def plot_trends_over_time(keywords, timeframe="today 12-m", per_page=3):
    num_keywords = len(keywords)
    num_pages = (
        num_keywords + per_page - 1
    ) // per_page  # Calculate the number of pages

    for page in range(num_pages):
        fig, axs = plt.subplots(nrows=per_page, ncols=1, figsize=(12, 5 * per_page))
        plt.subplots_adjust(hspace=0.5)
        for i in range(per_page):
            index = page * per_page + i
            if index >= num_keywords:
                # Hide empty subplots
                axs[i].axis("off")
                continue

            keyword = keywords[index]
            try:
                pytrends.build_payload(
                    [keyword], cat=0, timeframe=timeframe, geo="", gprop=""
                )
                interest_over_time_df = pytrends.interest_over_time()

                if not interest_over_time_df.empty:
                    axs[i].plot(
                        interest_over_time_df.index,
                        interest_over_time_df[keyword],
                        label=keyword,
                    )
                    axs[i].set_title(f"Interest in '{keyword}' over time")
                    axs[i].set_ylabel("Interest score")
                    axs[i].set_xlabel("Date")
                    axs[i].legend()
                else:
                    axs[i].text(
                        0.5,
                        0.5,
                        "No data",
                        horizontalalignment="center",
                        verticalalignment="center",
                        transform=axs[i].transAxes,
                    )
            except Exception as e:
                axs[i].text(
                    0.5,
                    0.5,
                    f"Error: {str(e)}",
                    horizontalalignment="center",
                    verticalalignment="center",
                    transform=axs[i].transAxes,
                )

        plt.tight_layout()
        plt.show()


# Function to fetch interest by platform for a keyword
def get_interest_by_platform(keyword, platform="web"):
    try:
        pytrends.build_payload(
            [keyword], cat=0, timeframe="now 1-d", geo="", gprop=platform
        )
        interest_by_platform_df = pytrends.interest_over_time()

        if not interest_by_platform_df.empty:
            print(f"\nInterest in '{keyword}' on platform '{platform}':")
            print(interest_by_platform_df.head(10).to_string())
            interest_by_platform_df.to_excel(
                f"{keyword}_interest_by_platform_{platform}.xlsx"
            )
        else:
            print(f"\nNo data for platform '{platform}' and keyword '{keyword}'")
    except Exception as e:
        print(f"\nUnable to fetch interest by platform for '{keyword}': {str(e)}")


# Example usage


def main():
    # List of countries to analyze
    countries = ["united_states", "poland", "germany", "france", "japan"]

    # Get top trending topics for each country
    for country in countries:
        get_top_trending_topics(country)

    # List of keywords to analyze
    keywords = ["Artificial Intelligence", "Machine Learning", "Blockchain"]

    # Analyze interest by region and related queries for each keyword
    for keyword in keywords:
        get_interest_by_region(keyword)
        get_related_queries(keyword)
        get_interest_over_time(keyword)

    # Generate plots for the keywords with pagination
    plot_trends_over_time(keywords, timeframe="today 12-m", per_page=3)

    # Analyze interest on YouTube platform
    get_interest_by_platform("Artificial Intelligence", platform="youtube")

    # Analyze trends by category (e.g., category 7 for sports)
    get_trends_by_category("Football", category=7)


if __name__ == "__main__":
    main()
