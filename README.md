# 👻 Ghost Restaurant Detection — Zomato Bangalore
### MongoDB · Big Data · Saanvi Jain 

---

## 📌 Project Summary

Analysed **1,12,500 real Zomato Bangalore restaurant listings** stored in
MongoDB to automatically detect Ghost Restaurants or Cloud Kitchens — fake or inactive listings
that deceive customers on food delivery platforms.

A custom **Ghost Restaurant Scoring Algorithm** was built entirely using MongoDB operations.

---

## 🔑 Key Result

| Metric | Value |
|--------|-------|
| Total Restaurants Analysed | 1,12,500 |
| 🔴 Ghost Restaurants Detected | **39,374 (35%)** |
| 🟢 Legitimate Restaurants | **73,126 (65%)** |
| Average Rating (Bangalore) | 3.70 / 5 |
| Average Cost for Two | ₹555 |

> **1 in 3 Zomato Bangalore listings is a Ghost Restaurant.**

---

## 🗃️ Database Details

| Field | Value |
|-------|-------|
| Database | `ghost_restaurant_db` |
| Collection | `restaurants` |
| Total Records | 1,12,500 |
| Tool | MongoDB Compass + mongosh |
| Connection | localhost:27017 |
| Fields Added | `ghost_score` · `risk_level` · `is_ghost` |

---

## ✅ PROOF — MongoDB Running Live

### Database setup — 1,12,500 records confirmed
![Database Setup](screenshots/01_setup.png)

---

## 👻 Ghost Scoring Model

| Condition | Points | Reason |
|-----------|--------|--------|
| `book_table = No` | +1 | No physical dine-in presence |
| `online_order = No` | +1 | Not engaging customers digitally |
| `votes < 50` | +2 | Very low engagement — strongest signal |
| `votes 50–150` | +1 | Below average engagement |
| `rate < 3.0` | +2 | Very poor customer rating |
| `rate 3.0–3.5` | +1 | Below average quality |

**Score → Risk:**
- 0–1 = 🟢 Low (Legitimate)
- 2–3 = 🟡 Medium (Suspicious)
- 4+ = 🔴 High (Ghost Restaurant)

---

## 🔍 Filter Queries

### F1–F3: First 5 restaurants · Online ordering · Table booking
```js
db.restaurants.find({}).limit(5)
db.restaurants.find({ online_order: "Yes" }).limit(10)
db.restaurants.find({ book_table: "Yes" }).limit(10)
```
![Find Queries](screenshots/02_find_queries.png)

---

### F4–F5: Low rated (below 3.0) and Top rated (above 4.5)
```js
db.restaurants.find({ rate: { $lt: 3.0 } }).limit(10)
db.restaurants.find({ rate: { $gte: 4.5 } }).limit(10)
```
![Filter Queries](screenshots/03_filter_queries.png)

---

### F6: Ghost Pattern — No booking + No online order + votes below 50
```js
db.restaurants.find({
  online_order: "No",
  book_table: "No",
  votes: { $lt: 50 }
})
```
![Ghost Pattern](screenshots/04_ghost_pattern.png)

---

### F7–F8: Affordable (under ₹300) and Expensive (above ₹2000)
```js
db.restaurants.find({
  "approx_cost(for two people)": { $lte: 300 }
}).limit(10)

db.restaurants.find({
  "approx_cost(for two people)": { $gte: 2000 }
}).limit(10)
```
![Cost Queries](screenshots/05_cost_queries.png)

---

## 📊 Aggregation Pipelines

### A1: Top 10 locations with most restaurants
```js
db.restaurants.aggregate([
  { $group: { _id: "$location", total_restaurants: { $sum: 1 } } },
  { $sort: { total_restaurants: -1 } },
  { $limit: 10 }
])
```
![Top Locations](screenshots/06_agg_location.png)

---

### A2: Average rating by restaurant type
```js
db.restaurants.aggregate([
  { $match: { rate: { $gt: 0 } } },
  { $group: {
      _id: "$rest_type",
      avg_rating: { $avg: "$rate" },
      total: { $sum: 1 }
  }},
  { $sort: { avg_rating: -1 } },
  { $limit: 10 }
])
```
![Rating by Type](screenshots/07_agg_rating.png)

---

### A4: Online Order vs No Online Order — KEY FINDING
> Restaurants with online ordering have higher average ratings.
> Proves digital engagement is a legitimacy signal.

```js
db.restaurants.aggregate([
  { $match: { rate: { $gt: 0 } } },
  { $group: {
      _id: "$online_order",
      avg_rating:  { $avg: "$rate" },
      avg_votes:   { $avg: "$votes" },
      total_count: { $sum: 1 }
  }}
])
```
![Online Order vs Rating](screenshots/08_agg_online_order.png)

---

### A5: Table Booking vs No Booking — KEY FINDING
> Booking restaurants: **4.14 avg rating** vs **3.62** without.
> **6x more votes.** Strongest single legitimacy indicator.

```js
db.restaurants.aggregate([
  { $match: { rate: { $gt: 0 } } },
  { $group: {
      _id: "$book_table",
      avg_rating:  { $avg: "$rate" },
      avg_votes:   { $avg: "$votes" },
      total_count: { $sum: 1 }
  }}
])
```
![Table Booking vs Rating](screenshots/09_agg_table_booking.png)

---

### A6: Top 10 most popular cuisines in Bangalore
```js
db.restaurants.aggregate([
  { $group: { _id: "$cuisines", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```
![Top Cuisines](screenshots/15_agg_cuisines.png)

---

### A7: Restaurant type distribution
```js
db.restaurants.aggregate([
  { $group: { _id: "$rest_type", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```
![Restaurant Types](screenshots/16_agg_rest_type.png)

---

### A8: Count by listing category type
```js
db.restaurants.aggregate([
  { $group: { _id: "$listed_in(type)", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```
![Category Types](screenshots/17_agg_category_type.png)

---

## 👻 Ghost Detection — Update Operations

### U1: Ghost score calculated and assigned to ALL 1,12,500 restaurants
```js
db.restaurants.find({}).forEach(function(doc) {
  let score = 0;
  if (doc.book_table === "No")   score += 1;
  if (doc.online_order === "No") score += 1;
  if (doc.votes < 50)            score += 2;
  else if (doc.votes < 150)      score += 1;
  if (doc.rate < 3.0)            score += 2;
  else if (doc.rate < 3.5)       score += 1;

  let risk = "Low";
  if (score >= 4)      risk = "High";
  else if (score >= 2) risk = "Medium";

  db.restaurants.updateOne(
    { _id: doc._id },
    { $set: { ghost_score: score, risk_level: risk } }
  );
});
```
![Ghost Scoring Running](screenshots/10_ghost_scoring.png)

---

### U2: Flag all High risk as ghost = true
```js
db.restaurants.updateMany(
  { risk_level: "High" },
  { $set: { is_ghost: true } }
)
// modifiedCount: 39374
```
![Flag Ghost](screenshots/18_flag_ghost.png)

---

### U3: Flag Low and Medium risk as legitimate
```js
db.restaurants.updateMany(
  { risk_level: { $in: ["Low", "Medium"] } },
  { $set: { is_ghost: false } }
)
// modifiedCount: 73126
```
![Flag Legit](screenshots/19_flag_legit.png)

---

### U4: Verify final counts
```js
db.restaurants.countDocuments({ is_ghost: true })   // 39374
db.restaurants.countDocuments({ is_ghost: false })  // 73126
```
![Ghost Counts](screenshots/11_ghost_counts.png)

---

### U5: View a sample ghost restaurant document
```js
db.restaurants.findOne({ is_ghost: true })
// ghost_score: 4+ · risk_level: "High" · is_ghost: true
```
![Sample Ghost](screenshots/20_sample_ghost.png)

---

### U6: View a sample legitimate restaurant document
```js
db.restaurants.findOne({ is_ghost: false })
// ghost_score: 0-1 · risk_level: "Low" · is_ghost: false
```
![Sample Legit](screenshots/21_sample_legit.png)

---

## 🔑 Indexes Created

```js
db.restaurants.createIndex({ location: 1 })
db.restaurants.createIndex({ rate: -1 })
db.restaurants.createIndex({ votes: -1 })
db.restaurants.createIndex({ online_order: 1, book_table: 1, votes: 1 })
db.restaurants.createIndex({ ghost_score: -1 })
db.restaurants.getIndexes()
```
![Indexes](screenshots/12_indexes.png)

---

## 🏁 Final Aggregation Queries

### FINAL 1: Ghost vs Legitimate full breakdown
```js
db.restaurants.aggregate([
  { $group: {
      _id: "$risk_level",
      total_count: { $sum: 1 },
      avg_rating:  { $avg: "$rate" },
      avg_votes:   { $avg: "$votes" },
      avg_cost:    { $avg: "$approx_cost(for two people)" }
  }},
  { $sort: { total_count: -1 } }
])
```
![Final 1 Breakdown](screenshots/22_final1_breakdown.png)

---

### FINAL 2: Top 10 locations with most ghost restaurants
```js
db.restaurants.aggregate([
  { $match: { is_ghost: true } },
  { $group: { _id: "$location", ghost_count: { $sum: 1 } } },
  { $sort: { ghost_count: -1 } },
  { $limit: 10 }
])
// BTM Layout = 4458 ghost restaurants
```
![Final 2 Ghost Locations](screenshots/23_final2_ghost_locations.png)

---

### FINAL 3: Top 10 locations with most legitimate restaurants
```js
db.restaurants.aggregate([
  { $match: { is_ghost: false } },
  { $group: { _id: "$location", legit_count: { $sum: 1 } } },
  { $sort: { legit_count: -1 } },
  { $limit: 10 }
])
```
![Final 3 Legit Locations](screenshots/24_final3_legit_locations.png)

---

### FINAL 4: Which cuisines are most common in ghost restaurants
```js
db.restaurants.aggregate([
  { $match: { is_ghost: true } },
  { $group: { _id: "$cuisines", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```
![Final 4 Ghost Cuisines](screenshots/25_final4_ghost_cuisines.png)

---

### FINAL 5: Ghost restaurant percentage out of total
```js
db.restaurants.aggregate([
  { $group: { _id: "$is_ghost", count: { $sum: 1 } } }
])
// false = 73126 (65%) · true = 39374 (35%)
```
![Final 5 Percentage](screenshots/26_final5_percentage.png)

---

### FINAL 6: Best rated locations in Bangalore
```js
db.restaurants.aggregate([
  { $match: { rate: { $gt: 0 } } },
  { $group: {
      _id: "$location",
      avg_rating: { $avg: "$rate" },
      total: { $sum: 1 }
  }},
  { $match: { total: { $gt: 10 } } },
  { $sort: { avg_rating: -1 } },
  { $limit: 10 }
])
```
![Final 6 Best Locations](screenshots/27_final6_best_locations.png)

---

### FINAL 7: Overall project summary stats
```js
db.restaurants.aggregate([
  { $group: {
      _id: null,
      total_restaurants:    { $sum: 1 },
      avg_rating_bangalore: { $avg: "$rate" },
      avg_cost_bangalore:   { $avg: "$approx_cost(for two people)" },
      total_ghost: { $sum: { $cond: [{ $eq: ["$is_ghost", true]  }, 1, 0] } },
      total_legit: { $sum: { $cond: [{ $eq: ["$is_ghost", false] }, 1, 0] } }
  }}
])
// total=112500 · ghost=39374 · legit=73126 · avg_rating=3.70 · avg_cost=₹555
```
![Final 7 Summary](screenshots/13_final_summary.png)

---

## 📈 Python Data Visualisations

> Generated using Python (matplotlib + pymongo) by directly
> querying the live MongoDB database.
> Full code in `visualisation.py`

![All 6 Charts](screenshots/14_charts.png)

- **Chart 1** — 35% Ghost vs 65% Legitimate (Pie Chart)
- **Chart 2** — Average rating drops as risk level increases
- **Chart 3** — Top 10 Bangalore locations by restaurant count
- **Chart 4** — Online ordering restaurants have higher ratings
- **Chart 5** — Ghost score distribution across all 1,12,500 restaurants
- **Chart 6** — Top 10 cuisines in Bangalore

---

## 📋 Key Findings

| # | Finding | Proof |
|---|---------|-------|
| 1 | **35% of listings are Ghost Restaurants** | 39,374 out of 1,12,500 flagged |
| 2 | **Table booking = strongest legitimacy signal** | 4.14 vs 3.62 rating · 6x more votes |
| 3 | **Online ordering correlates with quality** | Yes=3.72 avg · No=3.66 avg |
| 4 | **BTM Layout has most ghost restaurants** | 4,458 ghost listings |
| 5 | **North Indian cuisine dominates listings** | Highest count in both ghost and legit |

---

## 📁 Files in This Repository

| File | Description |
|------|-------------|
| `README.md` | Full project — all queries, results, screenshots |
| `visualisation.py` | Python code that generated all 6 charts |
| `screenshots/` | 27 screenshots of real MongoDB terminal output |
