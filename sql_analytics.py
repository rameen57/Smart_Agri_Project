import pandas as pd
import sqlite3

df = pd.read_csv("final_agriculture_crisis_dataset.csv")

conn = sqlite3.connect(":memory:")
df.to_sql("agriculture", conn, index=False, if_exists="replace")

queries = {
    "Top crops by pesticide usage": """
        SELECT Crop, ROUND(SUM(Pesticide_Usage), 2) AS Total_Pesticide_Usage
        FROM agriculture
        GROUP BY Crop
        ORDER BY Total_Pesticide_Usage DESC
        LIMIT 10;
    """,

    "Crop production summary": """
        SELECT Crop,
               ROUND(AVG(Production_Thousand_Tons), 2) AS Avg_Production,
               ROUND(MAX(Production_Thousand_Tons), 2) AS Max_Production,
               ROUND(MIN(Production_Thousand_Tons), 2) AS Min_Production
        FROM agriculture
        GROUP BY Crop
        ORDER BY Avg_Production DESC
        LIMIT 10;
    """,

    "Crisis risk count": """
        SELECT Crisis_Level, COUNT(*) AS Total_Records
        FROM agriculture
        GROUP BY Crisis_Level
        ORDER BY Total_Records DESC;
    """,

    "Cropped area analysis": """
        SELECT Crop,
               ROUND(AVG(Cropped_Area), 2) AS Avg_Cropped_Area,
               ROUND(AVG(Area_Percent), 2) AS Avg_Area_Percent
        FROM agriculture
        GROUP BY Crop
        ORDER BY Avg_Cropped_Area DESC
        LIMIT 10;
    """
}

for name, query in queries.items():
    print("\n==========", name.upper(), "==========")
    result = pd.read_sql_query(query, conn)
    print(result)

    filename = name.lower().replace(" ", "_") + ".csv"
    result.to_csv(filename, index=False)

conn.close()

print("\nSQL analytics completed successfully.")