import pandas as pd
import numpy as np

URL = "https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29"

# 1) Pull ALL HTML tables from the page
tables = pd.read_html(URL, flavor="html5lib")

# 2) Pick the table that has both 'country' and 'gdp' in its headers
gdp = None
for t in tables:
    cols = [str(c).lower() for c in t.columns]
    if any("country" in c for c in cols) and any("gdp" in c for c in cols):
        gdp = t.copy()
        break
if gdp is None:
    raise ValueError("Could not find a GDP table on the page.")

# 3) Rename the two columns we need to standard names
country_col = next(c for c in gdp.columns if "country" in str(c).lower())
gdp_col     = next(c for c in gdp.columns if "gdp"     in str(c).lower())
gdp = gdp.rename(columns={country_col: "Country", gdp_col: "GDP (Million USD)"})


s = gdp["GDP (Million USD)"].astype(str)
s = s.str.replace(",", "", regex=False)          # 1,234,567 → 1234567
s = s.str.replace(r"[^\d.\-]", "", regex=True)   # remove symbols/footnotes
gdp["GDP (Million USD)"] = pd.to_numeric(s, errors="coerce")
gdp = gdp.dropna(subset=["GDP (Million USD)"]).reset_index(drop=True)


gdp["GDP (Million USD)"] = gdp["GDP (Million USD)"].astype(int)   # (a) cast to int
gdp["GDP (Million USD)"] = gdp["GDP (Million USD)"] / 1000        # (b) million → billion
gdp["GDP (Million USD)"] = np.round(gdp["GDP (Million USD)"], 2)  # (c) round 2 decimals
gdp = gdp.rename(columns={"GDP (Million USD)": "GDP (Billion USD)"})  # (d) rename


gdp.to_csv("Largest_economies.csv", index=False)
print("Saved Largest_economies.csv")
print(gdp.head())
