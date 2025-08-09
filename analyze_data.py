#!/usr/bin/env python3
"""
Data cleaning, analysis and visualization script for FreeLytics job data.
Uses existing modules to avoid code redundancy.
"""

import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger

from src.job_offer_analyzer.DataframeAnalyzer import DataframeAnalyzer
from src.job_offer_cleaner.CSVLoader import CSVLoader
from src.job_offer_cleaner.DataframeCleaner import DataframeCleaner


def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    """Load and clean the CSV data using existing modules."""
    logger.info("Loading CSV data")
    df = CSVLoader.csv_to_pandas(csv_path)

    logger.info("Cleaning data using DataframeCleaner")

    # Remove duplicates
    df = DataframeCleaner.remove_duplicates(df)

    # Split revenue columns into min/max
    df = DataframeCleaner.split_revenue_to_min_max(df)

    # Clean publication dates
    df = DataframeCleaner.publication_date_cleaning(df)

    # Clean start dates
    df = DataframeCleaner.start_date_cleaning(df)

    # Standardize duration to days
    df = DataframeCleaner.standardize_duration(df)

    # Parse company description
    df = DataframeCleaner.parse_company_description(df)

    # One-hot encode contract types
    df = DataframeCleaner.contract_types_one_hot_encoding(df)

    logger.info(
        f"Data cleaning completed. Final dataset: {len(df)} rows, {len(df.columns)} columns"
    )
    return df


def perform_analysis(df: pd.DataFrame) -> dict:
    """Perform analysis using DataframeAnalyzer."""
    analyzer = DataframeAnalyzer(df)

    results = {
        "salary_min_stats": analyzer.get_salary_min_statistics_by_category(),
        "salary_max_stats": analyzer.get_salary_max_statistics_by_category(),
        "daily_rate_min_stats": analyzer.get_daily_rate_min_statistics_by_category(),
        "daily_rate_max_stats": analyzer.get_daily_rate_max_statistics_by_category(),
        "remote_work_proportions": analyzer.get_remote_work_proportions_by_category(),
        "experience_proportions": analyzer.get_experience_proportions_by_category(),
        "skills_frequency": analyzer.get_skills_frequency_by_category(),
        "cloud_provider_frequency": analyzer.get_cloud_provider_frequency_by_category(),
    }

    return results


def create_plots(df: pd.DataFrame, analysis_results: dict):
    """Create visualizations for the cleaned data."""
    plt.style.use("default")
    fig, axes = plt.subplots(3, 3, figsize=(20, 18))
    fig.suptitle("FreeLytics Job Market Analysis", fontsize=16, fontweight="bold")

    # 1. Salary distribution by job category
    ax1 = axes[0, 0]
    if not analysis_results["salary_min_stats"].empty:
        salary_data = analysis_results["salary_min_stats"]["mean"].dropna()
        if len(salary_data) > 0:
            salary_data.plot(kind="bar", ax=ax1, color="skyblue")
            ax1.set_title("Average Minimum Salary by Job Category")
            ax1.set_xlabel("Job Category")
            ax1.set_ylabel("Salary (€)")
            ax1.tick_params(axis="x", rotation=45)
        else:
            ax1.text(
                0.5,
                0.5,
                "No salary data available",
                ha="center",
                va="center",
                transform=ax1.transAxes,
            )
            ax1.set_title("Average Minimum Salary by Job Category")

    # 2. Daily rate distribution
    ax2 = axes[0, 1]
    if not analysis_results["daily_rate_min_stats"].empty:
        daily_rate_data = analysis_results["daily_rate_min_stats"]["mean"].dropna()
        if len(daily_rate_data) > 0:
            daily_rate_data.plot(kind="bar", ax=ax2, color="lightgreen")
            ax2.set_title("Average Minimum Daily Rate by Job Category")
            ax2.set_xlabel("Job Category")
            ax2.set_ylabel("Daily Rate (€)")
            ax2.tick_params(axis="x", rotation=45)
        else:
            ax2.text(
                0.5,
                0.5,
                "No daily rate data available",
                ha="center",
                va="center",
                transform=ax2.transAxes,
            )
            ax2.set_title("Average Minimum Daily Rate by Job Category")

    # 3. Remote work distribution
    ax3 = axes[1, 0]
    if not analysis_results["remote_work_proportions"].empty:
        remote_data = analysis_results["remote_work_proportions"]
        remote_data.plot(kind="bar", stacked=True, ax=ax3)
        ax3.set_title("Remote Work Options by Job Category")
        ax3.set_xlabel("Job Category")
        ax3.set_ylabel("Proportion")
        ax3.tick_params(axis="x", rotation=45)
        ax3.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    else:
        ax3.text(
            0.5,
            0.5,
            "No remote work data available",
            ha="center",
            va="center",
            transform=ax3.transAxes,
        )
        ax3.set_title("Remote Work Options by Job Category")

    # 4. Experience requirements
    ax4 = axes[1, 1]
    if not analysis_results["experience_proportions"].empty:
        exp_data = analysis_results["experience_proportions"]
        exp_data.plot(kind="bar", stacked=True, ax=ax4)
        ax4.set_title("Experience Requirements by Job Category")
        ax4.set_xlabel("Job Category")
        ax4.set_ylabel("Proportion")
        ax4.tick_params(axis="x", rotation=45)
        ax4.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    else:
        ax4.text(
            0.5,
            0.5,
            "No experience data available",
            ha="center",
            va="center",
            transform=ax4.transAxes,
        )
        ax4.set_title("Experience Requirements by Job Category")

    # 5. Top skills frequency
    ax5 = axes[2, 0]
    if not analysis_results["skills_frequency"].empty:
        skills_data = (
            analysis_results["skills_frequency"]
            .groupby("skill")["frequency"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        if len(skills_data) > 0:
            skills_data.plot(kind="bar", ax=ax5, color="orange")
            ax5.set_title("Top 10 Most Demanded Skills")
            ax5.set_xlabel("Skills")
            ax5.set_ylabel("Frequency")
            ax5.tick_params(axis="x", rotation=45)
        else:
            ax5.text(
                0.5,
                0.5,
                "No skills data available",
                ha="center",
                va="center",
                transform=ax5.transAxes,
            )
            ax5.set_title("Top 10 Most Demanded Skills")

    # 6. Contract types distribution
    ax6 = axes[2, 0]
    contract_cols = [
        col for col in df.columns if col.startswith("contract_") and col != "contract_types"
    ]
    if contract_cols:
        # Sum boolean columns
        contract_sums = df[contract_cols].sum().sort_values(ascending=False)
        contract_sums.index = [col.replace("contract_", "") for col in contract_sums.index]
        if len(contract_sums) > 0:
            contract_sums.plot(kind="bar", ax=ax6, color="purple")
            ax6.set_title("Contract Types Distribution")
            ax6.set_xlabel("Contract Type")
            ax6.set_ylabel("Number of Jobs")
            ax6.tick_params(axis="x", rotation=45)
        else:
            ax6.text(
                0.5,
                0.5,
                "No contract data available",
                ha="center",
                va="center",
                transform=ax6.transAxes,
            )
            ax6.set_title("Contract Types Distribution")
    else:
        ax6.text(
            0.5,
            0.5,
            "No contract type data available",
            ha="center",
            va="center",
            transform=ax6.transAxes,
        )
        ax6.set_title("Contract Types Distribution")

    # 7. Cloud providers distribution
    ax7 = axes[2, 1]
    if not analysis_results["cloud_provider_frequency"].empty:
        cloud_data = (
            analysis_results["cloud_provider_frequency"]
            .groupby("cloud_provider")["frequency"]
            .sum()
            .sort_values(ascending=False)
        )
        if len(cloud_data) > 0:
            cloud_data.plot(kind="bar", ax=ax7, color=["#FF9500", "#007ACC", "#4285F4"])
            ax7.set_title("Cloud Providers Demand")
            ax7.set_xlabel("Cloud Provider")
            ax7.set_ylabel("Frequency")
            ax7.tick_params(axis="x", rotation=45)
        else:
            ax7.text(
                0.5,
                0.5,
                "No cloud provider data available",
                ha="center",
                va="center",
                transform=ax7.transAxes,
            )
            ax7.set_title("Cloud Providers Demand")
    else:
        ax7.text(
            0.5,
            0.5,
            "No cloud provider data available",
            ha="center",
            va="center",
            transform=ax7.transAxes,
        )
        ax7.set_title("Cloud Providers Demand")

    # Hide the unused subplot
    axes[2, 2].set_visible(False)

    plt.tight_layout()
    plt.savefig("plots/data_analysis_plots.png", dpi=300, bbox_inches="tight")
    plt.show()

    logger.info("Plots saved as 'plots/data_analysis_plots.png'")


def main():
    """Main function to run the complete analysis pipeline."""
    csv_path = "data/scrap.csv"

    try:
        # Load and clean data
        logger.info("Starting data cleaning and analysis pipeline")
        cleaned_df = load_and_clean_data(csv_path)

        # Perform analysis
        logger.info("Performing statistical analysis")
        analysis_results = perform_analysis(cleaned_df)

        # Display key statistics
        print("\n=== DATA CLEANING SUMMARY ===")
        print(f"Total jobs after cleaning: {len(cleaned_df)}")
        print(f"Total columns: {len(cleaned_df.columns)}")
        print(f"Job categories: {cleaned_df['job_category'].nunique()}")

        print("\n=== SALARY STATISTICS BY CATEGORY ===")
        if not analysis_results["salary_min_stats"].empty:
            print(analysis_results["salary_min_stats"])
        else:
            print("No salary data available")

        print("\n=== DAILY RATE STATISTICS BY CATEGORY ===")
        if not analysis_results["daily_rate_min_stats"].empty:
            print(analysis_results["daily_rate_min_stats"])
        else:
            print("No daily rate data available")

        print("\n=== TOP 10 SKILLS ===")
        if not analysis_results["skills_frequency"].empty:
            top_skills = (
                analysis_results["skills_frequency"]
                .groupby("skill")["frequency"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )
            print(top_skills)
        else:
            print("No skills data available")

        print("\n=== CLOUD PROVIDERS DEMAND ===")
        if not analysis_results["cloud_provider_frequency"].empty:
            cloud_demand = (
                analysis_results["cloud_provider_frequency"]
                .groupby("cloud_provider")["frequency"]
                .sum()
                .sort_values(ascending=False)
            )
            print(cloud_demand)
        else:
            print("No cloud provider data available")

        # Create visualizations
        logger.info("Creating visualizations")
        create_plots(cleaned_df, analysis_results)

        logger.info("Analysis completed successfully!")

    except Exception as e:
        logger.error(f"Error in analysis pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    main()
