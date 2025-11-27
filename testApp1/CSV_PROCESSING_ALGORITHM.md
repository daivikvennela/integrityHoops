# CSV Processing Algorithm

## Overview
This document describes the complete algorithm for processing game CSV files from raw input to fully processed database records with calculated statistics.

---

## Input Requirements

### CSV File Format
- **Filename Convention**: `MM.DD.YY TEAM v OPPONENT.csv`
  - Example: `10.28.25 MIA v CHA-Table 1.csv`
  - Supports single-digit months/days: `11.2.25`
  
- **CSV Structure**:
  - Optional first line: `"Table 1"` (will be skipped if present)
  - Header row with required columns:
    - `Timeline`, `Start time`, `Duration`, `Row`, `Instance number`
    - Category columns: `Cutting & Screeing`, `DM Catch`, `Driving`, `Finishing`, `Footwork`, `Passing`, `Positioning`, `QB12 DM`, `Relocation`, `Space Read`, `Transition`
  - Data rows with `Row` column containing team/player names

---

## Processing Pipeline

### Phase 1: Validation

**Step 1.1: File Validation**
```
INPUT: CSV file path
VALIDATE:
  - File exists
  - File has .csv extension
  - File is readable
OUTPUT: Validation result (pass/fail)
```

**Step 1.2: Filename Parsing**
```
INPUT: Filename string
EXTRACT:
  - Date (MM.DD.YY format)
  - Team name
  - Opponent name
NORMALIZE:
  - Pad single-digit months/days with zero
  - Example: "11.2.25" → "11.02.25"
OUTPUT: {date_string, team, opponent}
```

**Step 1.3: Duplicate Detection**
```
INPUT: {date_string, team}
GENERATE: game_id = SHA256(date_string + "_" + team)[:16]
CHECK: Database for existing game_id
OUTPUT: exists (true/false)
CONSTRAINT: Only ONE game per team per date
```

---

### Phase 2: Preprocessing (CSV Splitting)

**Step 2.1: Load CSV**
```
INPUT: CSV file path
PROCESS:
  1. Check first line for "Table 1"
  2. Skip first line if "Table 1" found
  3. Read CSV with proper encoding (UTF-8, fallback to latin-1)
  4. Verify "Row" column exists
OUTPUT: DataFrame with all rows and columns
```

**Step 2.2: Extract Metadata**
```
INPUT: DataFrame
EXTRACT from first row "Timeline" column:
  - Date (MM.DD.YY TEAM v OPPONENT Team format)
  - Parse opponent if not in filename
OUTPUT: {date, opponent, team}
```

**Step 2.3: Split by Row (Group By)**
```
INPUT: DataFrame with "Row" column
PROCESS:
  1. Get unique values from "Row" column
  2. For each unique value:
     - Filter DataFrame rows matching that value
     - Create separate DataFrame
     - Save to temp CSV file
OUTPUT:
  - team_csv: CSV for team data (Row = team name)
  - player_csvs: Dict of {player_name: csv_path}
```

---

### Phase 3: Cognitive Score Calculation

**Step 3.1: Count Positive/Negative Indicators**
```
INPUT: CSV DataFrame
FOR EACH category column:
  FOR EACH pattern in column_mappings[category]:
    COUNT occurrences of "+ve [pattern]" → positive_count
    COUNT occurrences of "-ve [pattern]" → negative_count
    
EXAMPLE (Footwork column):
  "+ve Footwork: Step to Ball" → footwork_step_to_ball_positive
  "-ve Footwork: Patient Pickup" → footwork_patient_pickup_negative
  
OUTPUT: stats_dict = {
  'footwork_step_to_ball_positive': 12,
  'footwork_step_to_ball_negative': 11,
  'passing_teammate_on_move_positive': 29,
  ...
}
```

**Step 3.2: Calculate Category Scores**
```
INPUT: stats_dict from Step 3.1
FOR EACH category:
  positive_total = SUM(all positive fields for category)
  negative_total = SUM(all negative fields for category)
  
  IF (positive_total + negative_total) > 0:
    percentage = (positive_total / (positive_total + negative_total)) * 100
  ELSE:
    percentage = None
    
OUTPUT: category_scores = {
  'Footwork': 52.17%,    // (12 / (12+11)) * 100
  'Passing': 95.12%,     // (29+11) / (29+11+2+1) * 100
  ...
}
```

**Step 3.3: Calculate Overall Cognitive Score**
```
INPUT: All category scores
PROCESS:
  valid_scores = [score for score in category_scores if score is not None]
  overall_score = AVERAGE(valid_scores)
  
OUTPUT: overall_cog_score = 74.71%
```

---

### Phase 4: Create Scorecard Objects

**Step 4.1: Instantiate Scorecard**
```
INPUT: stats_dict from Phase 3
CREATE: Scorecard object
  player_name = team_name or player_name
  game_id = generated_game_id
  date_created = current_timestamp
  **stats_dict  // Unpack all stat fields
  
FIELDS (78 total):
  - 2 Space Read fields (positive/negative)
  - 10 DM Catch fields
  - 14 QB12 fields
  - 4 Driving fields
  - 4 Positioning fields
  - 2 Transition fields
  - 10 Cutting & Screening fields
  - 14 Relocation fields
  - 6 Footwork fields (⭐ NEW)
  - 4 Passing fields (⭐ NEW)
  - 12 Finishing fields (⭐ NEW)
  
OUTPUT: Scorecard object with all fields populated
```

---

### Phase 5: Database Storage

**Step 5.1: Create Game Record**
```
INPUT: {game_id, date, date_string, team, opponent}
INSERT INTO games:
  - id = game_id (unique, 16-char hex)
  - date = timestamp
  - date_string = "MM.DD.YY"
  - team = team name
  - opponent = opponent name
  - created_at = current_timestamp
  
CONSTRAINT: UNIQUE(game_id)
OUTPUT: Game record created
```

**Step 5.2: Create Player Record (if not exists)**
```
INPUT: player_name
CHECK: SELECT FROM players WHERE name = player_name
IF NOT EXISTS:
  INSERT INTO players (name, date_created)
OUTPUT: Player record ensured
```

**Step 5.3: Store Scorecard**
```
INPUT: Scorecard object
INSERT INTO scorecards:
  - player_name (foreign key)
  - game_id (foreign key)
  - date_created
  - space_read_live_dribble, space_read_catch, ...
  - [78 stat fields]
  - footwork_step_to_ball_positive, ...
  - passing_teammate_on_move_positive, ...
  - finishing_stride_pivot_positive, ...
  
OUTPUT: Scorecard record created
```

**Step 5.4: Store Team Cognitive Score**
```
INPUT: {game_date, team, opponent, overall_cog_score}
INSERT INTO team_cog_scores:
  - game_date (timestamp)
  - team
  - opponent
  - score (overall_cog_score)
  - note
  
CONSTRAINT: UNIQUE(game_date, team, opponent)
OUTPUT: Team cog score record created
```

**Step 5.5: Store Team Statistics (Per Category)**
```
INPUT: {game_date_iso, team, opponent, category_scores}
FOR EACH category in category_scores:
  GET positive_count, negative_count from scorecard
  
  INSERT INTO team_statistics:
    - game_date_iso (YYYY-MM-DD)
    - game_date_timestamp
    - date_string (MM.DD.YY)
    - team
    - opponent
    - category (e.g., "Footwork")
    - percentage (e.g., 52.17)
    - positive_count
    - negative_count
    - total_count
    - overall_score
    - csv_filename
    - calculated_at
    
CONSTRAINT: UNIQUE(game_date_iso, team, opponent, category)
OUTPUT: 10 statistics records created (one per category)
```

---

## Data Flow Diagram

```
┌─────────────────┐
│  Input CSV File │
│  "MM.DD.YY      │
│   TEAM v OPP"   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   VALIDATION    │
│  - File exists  │
│  - Format check │
│  - Duplicate?   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PREPROCESSING   │
│  - Skip Table 1 │
│  - Parse header │
│  - Split by Row │
└────────┬────────┘
         │
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ...
    │ Team   │  │Player 1│  │Player 2│
    │  CSV   │  │  CSV   │  │  CSV   │
    └───┬────┘  └───┬────┘  └───┬────┘
        │           │           │
        └───────────┴───────────┘
                    │
                    ▼
         ┌──────────────────┐
         │ SCORE CALCULATION│
         │  - Count +ve/-ve │
         │  - Calculate %   │
         │  - Overall score │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │CREATE SCORECARDS │
         │  - Team scorecard│
         │  - Player cards  │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ DATABASE STORAGE │
         │  - games         │
         │  - players       │
         │  - scorecards    │
         │  - team_cog_scores│
         │  - team_statistics│
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │     OUTPUT       │
         │  - game_id       │
         │  - cog_score     │
         │  - player_count  │
         └──────────────────┘
```

---

## Key Design Decisions

### 1. Game ID Generation
- **Formula**: `SHA256(date_string + "_" + team)[:16]`
- **Why**: Ensures deterministic, unique IDs based on date and team
- **Constraint**: One game per team per date

### 2. Pattern Matching with Regex Escaping
- **Issue**: Patterns like `"+ve"` contain regex special characters
- **Solution**: `re.escape(pattern)` before counting
- **Why**: Prevents regex errors with empty patterns

### 3. Category Field Aggregation
- **Issue**: Categories like "Footwork" have multiple sub-fields
- **Solution**: Sum all positive fields, sum all negative fields
- **Formula**: `percentage = (sum_positive / (sum_positive + sum_negative)) * 100`

### 4. Statistics Storage
- **Granularity**: One record per (game, category) combination
- **Why**: Allows flexible querying and chart generation
- **Result**: 9 games × 10 categories = 90 records

### 5. Duplicate Prevention
- **Method**: UNIQUE constraints on natural keys
- **Tables**:
  - `games`: UNIQUE(game_id)
  - `team_cog_scores`: UNIQUE(game_date, team, opponent)
  - `team_statistics`: UNIQUE(game_date_iso, team, opponent, category)

---

## Category Mappings

### Complete Field Mapping (78 fields)

| Category              | Positive Fields                          | Negative Fields                          |
|-----------------------|------------------------------------------|------------------------------------------|
| Space Read            | live_dribble, catch                      | live_dribble_negative, catch_negative    |
| DM Catch              | back_to_back, uncontested_shot, swing, drive_pass, drive_swing_skip_pass | (same, _negative) |
| QB12 DM               | strong_side, baseline, fill_behind, weak_side, roller, skip_pass, cutter | (same, _negative) |
| Driving               | paint_touch, physicality                 | (same, _negative)                        |
| Positioning           | create_shape, adv_awareness              | (same, _negative)                        |
| Transition            | effort_pace                              | effort_pace_negative                     |
| Cutting & Screening   | denial, movement, body_to_body, principle, cut_fill | (same, _negative) |
| Relocation            | weak_corner, 45_cut, slide_away, fill_behind, dunker_baseline, corner_fill, reverse_direction | (same, _negative) |
| **Footwork** ⭐        | step_to_ball, patient_pickup, long_2     | (same, _negative)                        |
| **Passing** ⭐         | teammate_on_move, read_length            | (same, _negative)                        |
| **Finishing** ⭐       | stride_pivot, read_length, ball_security, earn_foul, physicality, stride_holds, (+ driving_paint_touch) | (same, _negative) |

---

## Error Handling

### Common Errors and Solutions

1. **"CSV file missing 'Row' column"**
   - **Cause**: CSV doesn't have required "Row" column
   - **Solution**: Verify CSV has proper header structure

2. **"re.PatternError: nothing to repeat"**
   - **Cause**: Empty or invalid regex pattern
   - **Solution**: Use `re.escape(pattern)` before matching

3. **"Duplicate game"**
   - **Cause**: Game with same date and team already exists
   - **Solution**: Delete existing game or skip import

4. **"AttributeError: Scorecard has no attribute 'X'"**
   - **Cause**: New field not added to Scorecard model
   - **Solution**: Add field to `__init__`, instance assignments, and `to_dict()`

5. **"Duplicate team cog scores"**
   - **Cause**: Multiple inserts for same game
   - **Solution**: UNIQUE constraint prevents this; reprocessing creates duplicates
   - **Fix**: Clean duplicates, use `INSERT OR REPLACE`

---

## Performance Characteristics

- **Single CSV Processing**: ~2-5 seconds
- **Batch Processing (9 CSVs)**: ~20-30 seconds
- **Database Operations**: O(n) where n = number of records
- **Memory Usage**: O(m) where m = CSV file size (typically <10MB)

---

## Testing Recommendations

### Unit Tests
```python
def test_game_id_generation():
    # Verify deterministic ID generation
    id1 = generate_game_id("10.28.25", "Heat")
    id2 = generate_game_id("10.28.25", "Heat")
    assert id1 == id2
    assert len(id1) == 16

def test_scorecard_creation():
    # Verify all 78 fields are populated
    scorecard = create_scorecard_from_csv(csv_path, game_id, "Heat")
    assert scorecard.footwork_step_to_ball_positive >= 0
    assert scorecard.passing_teammate_on_move_positive >= 0

def test_statistics_calculation():
    # Verify percentage calculation
    stats = calculate_statistics([scorecard])
    assert 0 <= stats['Footwork'] <= 100
    assert 'Passing' in stats
```

### Integration Tests
```python
def test_full_pipeline():
    # Test complete CSV → Database flow
    result = importer.import_mega_csv(csv_path)
    assert result['success'] == True
    assert len(db.get_team_statistics()) == expected_count
```

---

## Future Enhancements

1. **Parallel Processing**: Process multiple CSVs concurrently
2. **Validation Schema**: JSON schema for CSV structure validation
3. **Incremental Updates**: Update only changed categories
4. **Audit Logging**: Track all database modifications
5. **Rollback Support**: Undo failed imports
6. **Data Versioning**: Track changes to scorecards over time

---

## Appendix: Example Data

### Input CSV (excerpt)
```csv
Timeline,Start time,Duration,Row,Instance number,Footwork,Passing,...
10.28.25 MIA v CHA Team,89.1,1.25,Miami Heat,1,,,,...
10.28.25 MIA v CHA Team,90.2,9.6,Miami Heat,2,,"+ve Passing: Teammate on the Move, +ve Passing: Read the Length",...
```

### Output Database Records

**games table:**
```sql
id: f90720964031c6ba
date: 1761634800
date_string: 10.28.25
team: Heat
opponent: CHA
```

**scorecards table:**
```sql
player_name: Heat
game_id: f90720964031c6ba
footwork_step_to_ball_positive: 12
footwork_patient_pickup_positive: 7
passing_teammate_on_move_positive: 29
passing_read_length_positive: 11
...
```

**team_cog_scores table:**
```sql
game_date: 1761634800
team: Heat
opponent: CHA
score: 77.95
```

**team_statistics table (10 records):**
```sql
date_string: 10.28.25, team: Heat, opponent: CHA, category: Footwork, percentage: 54.29
date_string: 10.28.25, team: Heat, opponent: CHA, category: Passing, percentage: 93.02
...
```

---

## Maintenance Notes

- **Database Schema**: Defined in `src/database/db_manager.py`
- **Scorecard Model**: Defined in `src/models/scorecard.py`
- **Processing Logic**: `src/processors/csv_to_database_importer.py`
- **Statistics Calculator**: `src/utils/statistics_calculator.py`
- **Validation**: `src/services/game_validator.py`

**Last Updated**: November 2025
**Version**: 2.0 (Added Footwork, Passing, and Finishing fields)

