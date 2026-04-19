import pymongo
import matplotlib.pyplot as plt

client = pymongo.MongoClient("mongodb://localhost:27017/")
db     = client["ghost_restaurant_db"]
col    = db["restaurants"]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Ghost Restaurant Detection — Zomato Bangalore",
             fontsize=16, fontweight="bold")

# Chart 1 — Ghost vs Legitimate
result1 = list(col.aggregate([
    {"$group": {"_id": "$is_ghost", "count": {"$sum": 1}}}
]))
labels1 = ["Ghost" if r["_id"] == True else "Legitimate" for r in result1]
size1   = [r["count"] for r in result1]
axes[0,0].pie(size1, labels=labels1,
              colors=["#e74c3c","#2ecc71"], autopct="%1.1f%%")
axes[0,0].set_title("Ghost vs Legitimate Restaurants")

# Chart 2 — Avg Rating by Risk Level
result2 = list(col.aggregate([
    {"$match": {"rate": {"$gt": 0}}},
    {"$group": {"_id": "$risk_level", "avg_rating": {"$avg": "$rate"}}},
    {"$sort": {"avg_rating": -1}}
]))
labels2 = [r["_id"] for r in result2]
values2 = [round(r["avg_rating"], 2) for r in result2]
bars2   = axes[0,1].bar(labels2, values2,
                        color=["#2ecc71","#f39c12","#e74c3c"],
                        edgecolor="black")
axes[0,1].set_title("Avg Rating by Risk Level")
axes[0,1].set_ylim(0, 5)
for bar, val in zip(bars2, values2):
    axes[0,1].text(bar.get_x() + bar.get_width()/2,
                   bar.get_height() + 0.05,
                   str(val), ha="center", fontweight="bold")

# Chart 3 — Top 10 Locations
result3 = list(col.aggregate([
    {"$group": {"_id": "$location", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
]))
labels3 = [r["_id"] if r["_id"] else "Unknown" for r in result3]
values3 = [r["count"] for r in result3]
axes[0,2].barh(labels3[::-1], values3[::-1],
               color="#3498db", edgecolor="black")
axes[0,2].set_title("Top 10 Locations by Restaurant Count")

# Chart 4 — Online Order vs Avg Rating
result4 = list(col.aggregate([
    {"$match": {"rate": {"$gt": 0}}},
    {"$group": {"_id": "$online_order", "avg_rating": {"$avg": "$rate"}}}
]))
labels4 = ["Online: " + str(r["_id"]) for r in result4]
values4 = [round(r["avg_rating"], 2) for r in result4]
colors4 = ["#e74c3c" if r["_id"] == "No" else "#2ecc71" for r in result4]
bars4   = axes[1,0].bar(labels4, values4, color=colors4, edgecolor="black")
axes[1,0].set_title("Online Order vs Avg Rating")
axes[1,0].set_ylim(0, 5)
for bar, val in zip(bars4, values4):
    axes[1,0].text(bar.get_x() + bar.get_width()/2,
                   bar.get_height() + 0.05,
                   str(val), ha="center", fontweight="bold")

# Chart 5 — Ghost Score Distribution
result5 = list(col.aggregate([
    {"$group": {"_id": "$ghost_score", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]))
labels5 = ["Score " + str(r["_id"]) for r in result5]
values5 = [r["count"] for r in result5]
axes[1,1].bar(labels5, values5, color="#9b59b6", edgecolor="black")
axes[1,1].set_title("Ghost Score Distribution")
axes[1,1].set_ylabel("Number of Restaurants")

# Chart 6 — Top 10 Cuisines
result6 = list(col.aggregate([
    {"$group": {"_id": "$cuisines", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 10}
]))
labels6 = [str(r["_id"])[0:20] if r["_id"] else "Unknown" for r in result6]
values6 = [r["count"] for r in result6]
axes[1,2].barh(labels6[::-1], values6[::-1],
               color="#e67e22", edgecolor="black")
axes[1,2].set_title("Top 10 Cuisines")

plt.tight_layout()
plt.savefig("ghost_restaurant_charts.png", dpi=150, bbox_inches="tight")
plt.show()
print("Done! Charts saved.")
