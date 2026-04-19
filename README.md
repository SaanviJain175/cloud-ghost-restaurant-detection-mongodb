# 👻 Ghost Restaurant Detection — Zomato Bangalore (Kaggle)
### MongoDB · Big Data · Saanvi Jain

## 📌 Project Summary

Analysed **1,12,500 real Zomato Bangalore restaurant listings** stored in MongoDB
to automatically detect Ghost Restaurants or Cloud Kitchen — fake or inactive listings that
deceive customers on food delivery platforms.

Built a custom **Ghost Restaurant Scoring Algorithm** entirely using MongoDB operations.


## 🔑 Key Result

| Metric | Value |
|--------|-------|
| Total Restaurants Analysed | 1,12,500 |
| 🔴 Ghost Restaurants Detected | **39,374 (35%)** |
| 🟢 Legitimate Restaurants | **73,126 (65%)** |
| Average Rating (Bangalore) | 3.70 / 5 |
| Average Cost for Two | ₹555 |

> **1 in 3 Zomato Bangalore listings is a Ghost Restaurant.**

## ✅ PROOF — MongoDB Running Live

### Database Setup — 1,12,500 records confirmed in MongoDB
![Database Setup](screenshots/01_setup.png)

---

## 👻 Ghost Scoring Model

Each restaurant gets points based on 6 conditions:

| Condition | Points | Reason |
|-----------|--------|--------|
| `book_table = No` | +1 | No physical dine-in presence |
| `online_order = No` | +1 | Not engaging customers digitally |
| `votes < 50` | +2 | Very low engagement — strongest signal |
| `votes 50–150` | +1 | Below average engagement |
| `rate < 3.0` | +2 | Very poor customer rating |
| `rate 3.0–3.5` | +1 | Below average quality |

**Score → Risk Level:**
- 0–1 = 🟢 Low (Legitimate)
- 2–3 = 🟡 Medium (Suspicious)
- 4+ = 🔴 High (Ghost Restaurant)

---

## 🔍 MongoDB Filter Queries

### F1–F3: Basic finds — first 5 restaurants, online ordering, table booking
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
      avg_rating: { $avg: "$rate" },
      avg_votes:  { $avg: "$votes" },
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
      avg_rating: { $avg: "$rate" },
      avg_votes:  { $avg: "$votes" },
      total_count: { $sum: 1 }
  }}
])
```
![Table Booking vs Rating](screenshots/09_agg_table_booking.png)

---

## 👻 Ghost Detection — Update Operations

### U1: Score assigned to ALL 1,12,500 restaurants
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

### U2–U4: Flag ghost vs legitimate + verify counts
```js
db.restaurants.updateMany(
  { risk_level: "High" },
  { $set: { is_ghost: true } }
)
db.restaurants.updateMany(
  { risk_level: { $in: ["Low","Medium"] } },
  { $set: { is_ghost: false } }
)
// Verify:
db.restaurants.countDocuments({ is_ghost: true })   // → 39374
db.restaurants.countDocuments({ is_ghost: false })  // → 73126
```
![Ghost Flag Results](screenshots/11_ghost_counts.png)

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

## 🏁 Final Summary Query
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
// Result: total=112500, ghost=39374, legit=73126
```
![Final Summary](screenshots/13_final_summary.png)

---

## 📈 Python Data Visualisations

> Generated using Python (matplotlib + pymongo) by directly
> querying the live MongoDB database. See `visualisation.py`

![All 6 Charts](screenshots/14_charts.png)

**Charts:**
- Chart 1 — 35% Ghost vs 65% Legitimate (Pie)
- Chart 2 — Average rating drops as risk increases (Bar)
- Chart 3 — Top 10 Bangalore locations by count (Bar)
- Chart 4 — Online ordering = higher ratings (Bar)
- Chart 5 — Ghost score distribution across 1,12,500 restaurants
- Chart 6 — Top 10 cuisines in Bangalore

---

## 📋 Key Findings

| # | Finding | Proof |
|---|---------|-------|
| 1 | **35% of listings are Ghost Restaurants** | 39,374 flagged out of 1,12,500 |
| 2 | **Table booking = strongest legitimacy signal** | 4.14 vs 3.62 rating · 6x more votes |
| 3 | **Online ordering correlates with quality** | Yes=3.72 avg · No=3.66 avg |
| 4 | **BTM Layout has most ghost restaurants** | 4,458 ghost listings |
| 5 | **North Indian cuisine dominates listings** | Highest count in both ghost and legit |

---

## 🗃️ Database Details

| Field | Value |
|-------|-------|
| Database | `ghost_restaurant_db` |
| Collection | `restaurants` |
| Records | 1,12,500 |
| Tool | MongoDB Compass + mongosh |
| Connection | localhost:27017 |
| Fields Added | `ghost_score`, `risk_level`, `is_ghost` |

---

## 👩‍💻 Submitted By

**Saanvi Jain** | Roll No: 24215409 | 4EDA
Big Data CIA-3 | Prof. Indu Verma | School of Sciences
