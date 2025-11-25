import pandas as pd
import matplotlib.pyplot as plt

# Example: create a small chart from a made-up day's comfort scores
data = pd.DataFrame({
    "hour": list(range(8, 21)),
    "comfort": [65,68,70,72,74,76,80,82,78,74,70,65,60]
})
data.to_csv("analysis/day_comfort.csv", index=False)

plt.figure()
plt.plot(data["hour"], data["comfort"])
plt.title("Comfort Score by Hour")
plt.xlabel("Hour"); plt.ylabel("Score")
plt.savefig("analysis/comfort_plot.png", dpi=150)
print("Wrote analysis/comfort_plot.png")
