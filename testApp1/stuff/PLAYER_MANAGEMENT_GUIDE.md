# 🏀 Player Management System

This guide explains the new Player and Scorecard management functionality added to the Basketball Cognitive Performance Dashboard.

## 📋 Overview

The Player Management System provides CRUD (Create, Read, Update, Delete) operations for basketball players and their associated scorecards. It includes:

- **Player Class**: Manages player information with name and creation date
- **Scorecard Class**: Tracks individual performance scorecards for players
- **Database Integration**: SQLite database with full CRUD operations
- **Web Interface**: Modern UI for managing players and scorecards
- **REST API**: Complete API endpoints for programmatic access

## 🏗️ Architecture

### Models

#### Player Class (`models/player.py`)
```python
class Player:
    def __init__(self, name: str, date_created: Optional[int] = None):
        self.name = name
        self.date_created = date_created or int(datetime.now().timestamp())
        self.scorecards: List[Scorecard] = []
```

**Attributes:**
- `name` (str): Player's name
- `date_created` (int): Unix timestamp of creation
- `scorecards` (List[Scorecard]): Associated scorecards

**Methods:**
- `add_scorecard(scorecard)`: Add a scorecard to the player
- `remove_scorecard(scorecard)`: Remove a scorecard
- `get_scorecards()`: Get all scorecards
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary

#### Scorecard Class (`models/scorecard.py`)
```python
class Scorecard:
    def __init__(self, player_name: str, date_created: Optional[int] = None):
        self.player_name = player_name
        self.date_created = date_created or int(datetime.now().timestamp())
```

**Attributes:**
- `player_name` (str): Name of the player this scorecard belongs to
- `date_created` (int): Unix timestamp of creation

**Methods:**
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary

### Database

#### DatabaseManager (`database/db_manager.py`)
Handles all SQL operations using SQLite:

**Tables:**
- `players`: Stores player information
- `scorecards`: Stores scorecard information with foreign key to players

**CRUD Operations:**
- **Create**: `create_player()`, `create_scorecard()`
- **Read**: `get_player_by_name()`, `get_all_players()`, `get_scorecards_by_player()`
- **Update**: `update_player()`
- **Delete**: `delete_player()`, `delete_scorecard()`

## 🌐 Web Interface

### Access
Navigate to `/players` in your browser to access the Player Management interface.

### Features
- **Database Statistics**: Real-time stats showing player and scorecard counts
- **Create Players**: Simple form to add new players
- **Player Cards**: Visual cards showing each player with their scorecard count
- **Scorecard Management**: View and manage scorecards for each player
- **Delete Operations**: Remove players and scorecards with confirmation

### UI Components
- **Statistics Dashboard**: Shows database metrics
- **Create Player Form**: Add new players
- **Player Grid**: Displays all players in card format
- **Scorecard Modals**: View and manage scorecards
- **Create Scorecard Modal**: Add new scorecards with custom dates

## 🔌 REST API

### Endpoints

#### Players
- `GET /api/players` - Get all players
- `GET /api/players/<name>` - Get specific player
- `POST /api/players` - Create new player
- `PUT /api/players/<name>` - Update player
- `DELETE /api/players/<name>` - Delete player

#### Scorecards
- `GET /api/players/<name>/scorecards` - Get player's scorecards
- `POST /api/players/<name>/scorecards` - Create scorecard for player
- `DELETE /api/players/<name>/scorecards/<timestamp>` - Delete specific scorecard

#### Statistics
- `GET /api/stats` - Get database statistics

### Example API Usage

#### Create a Player
```bash
curl -X POST http://localhost:5001/api/players \
  -H "Content-Type: application/json" \
  -d '{"name": "LeBron James"}'
```

#### Get All Players
```bash
curl http://localhost:5001/api/players
```

#### Create a Scorecard
```bash
curl -X POST http://localhost:5001/api/players/LeBron%20James/scorecards \
  -H "Content-Type: application/json" \
  -d '{"date_created": 1754328000}'
```

#### Get Player Scorecards
```bash
curl http://localhost:5001/api/players/LeBron%20James/scorecards
```

## 🧪 Testing

### Test Script
Run the test script to verify functionality:

```bash
python3 test_models.py
```

This script tests:
1. Model creation and serialization
2. Database CRUD operations
3. Player and scorecard relationships
4. Error handling

### Manual Testing
1. **Create Players**: Use the web interface to add players
2. **Add Scorecards**: Create scorecards for players
3. **View Data**: Check that data persists and displays correctly
4. **Delete Operations**: Test deletion with confirmation dialogs

## 📁 File Structure

```
testApp1/
├── models/
│   ├── __init__.py
│   ├── player.py          # Player class
│   └── scorecard.py       # Scorecard class
├── database/
│   ├── __init__.py
│   └── db_manager.py      # Database operations
├── templates/
│   └── players.html       # Web interface
├── player_api.py          # REST API routes
├── test_models.py         # Test script
└── PLAYER_MANAGEMENT_GUIDE.md  # This guide
```

## 🔧 Configuration

### Database
- **Default**: SQLite database (`basketball.db`)
- **Location**: Project root directory
- **Auto-creation**: Tables created automatically on first run

### Web Interface
- **URL**: `http://localhost:5001/players`
- **Navigation**: Added to main navigation bar
- **Responsive**: Works on desktop and mobile

## 🚀 Usage Examples

### Creating a Player Programmatically
```python
from models import Player
from database import DatabaseManager

# Create player
player = Player("Stephen Curry")

# Save to database
db = DatabaseManager()
success = db.create_player(player)
```

### Adding a Scorecard
```python
from models import Scorecard

# Create scorecard
scorecard = Scorecard("Stephen Curry")

# Add to database
success = db.create_scorecard(scorecard)
```

### Retrieving Player Data
```python
# Get specific player
player = db.get_player_by_name("Stephen Curry")
print(f"Player: {player.name}")
print(f"Scorecards: {len(player.scorecards)}")

# Get all players
players = db.get_all_players()
for player in players:
    print(f"{player.name}: {len(player.scorecards)} scorecards")
```

## 🔒 Security Considerations

- **Input Validation**: All inputs are validated and sanitized
- **SQL Injection Protection**: Uses parameterized queries
- **Error Handling**: Comprehensive error handling and user feedback
- **Data Integrity**: Foreign key constraints maintain data relationships

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the correct directory
2. **Database Errors**: Check file permissions for database creation
3. **API Errors**: Verify the Flask application is running
4. **UI Issues**: Clear browser cache if interface doesn't update

### Debug Mode
Enable debug mode for detailed error messages:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 🔄 Future Enhancements

### Planned Features
- **Player Statistics**: Track performance metrics
- **Scorecard Templates**: Predefined scorecard types
- **Data Export**: Export player data to CSV/JSON
- **Advanced Search**: Search players by various criteria
- **Bulk Operations**: Import/export multiple players

### Extensibility
The modular design allows easy extension:
- Add new player attributes
- Create additional scorecard types
- Implement new database backends
- Add authentication and authorization

---

**Built with ❤️ using Flask, SQLite, and Bootstrap** 