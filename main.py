"""
File: main.py
Purpose: Entry point only
"""

import traceback
from core.pipeline import CustomerPipeline
from utils.file_utils import ensure_dir
import pandas as pd


def create_sample_data():
    ensure_dir("data")

    data = {
        'customer_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010,
                        1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020,
                        1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030,
                        1031, 1032, 1033, 1034, 1035, 1036],
        'age': [56, 69, 46, 32, 60, 25, 38, 56, 36, 40,
                28, 28, 41, 53, 57, 41, 20, 39, 19, 41,
                61, 47, 55, 19, 38, 50, 29, 39, 61, 42,
                66, 44, 59, 45, 33, 32],
        'total_purchases': [45, 1, 25, 7, 9, 24, 1, 44, 8, 24,
                            11, 17, 8, 35, 35, 33, 5, 42, 39, 31,
                            28, 7, 9, 8, 12, 34, 33, 48, 23, 24,
                            37, 35, 44, 40, 22, 27],
        'total_spent': [3477.56, 1383.59, 1258.42, 883.04, 1132.88, 2812.60,
                        2048.99, 371.22, 1306.88, 1272.04, 3496.71, 3575.74,
                        783.03, 4988.82, 1370.57, 4884.24, 2084.63, 213.60,
                        1758.10, 3190.04, 3419.49, 2678.13, 2266.53, 2786.82,
                        2983.85, 450.22, 1879.79, 1248.69, 4025.54, 2377.99,
                        4917.94, 2024.18, 4091.34, 4001.81, 796.05, 2565.58]
    }

    df = pd.DataFrame(data)
    csv_path = "data/customers.csv"
    json_path = "data/customers.json"
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient='records')

    print(f"Created {csv_path} with {len(df)} rows")
    print(f"Created {json_path}")

    return csv_path, json_path


def main():
    print("\n" + "=" * 60)
    print("STARTING CUSTOMER PIPELINE")
    print("=" * 60)

    try:
        csv_path, _ = create_sample_data()

        pipeline = CustomerPipeline()
        result = pipeline.run_from_csv(csv_path)

        if result is not None:
            print("\n✅ Pipeline completed successfully!")
            print("Check the 'outputs/' folder for results")
        else:
            print("\n❌ Pipeline failed")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()