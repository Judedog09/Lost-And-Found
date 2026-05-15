# Academy Finder — Lost & Found

A web-based lost and found system built for Albuquerque Academy. Staff log found items into a shared database, and students can search for their belongings and claim them online.

---

## Problem Being Solved

Albuquerque Academy's lost and found process was entirely manual — students had to physically visit the office to check if something had been turned in, and staff had no central place to track what was in their possession or who had already claimed it. Academy Finder digitizes this process so students can search from anywhere and staff can manage inventory from a single dashboard.

---

## Features & Functionality

**Student View (`/`)**
- Search the item database in real time by name or description
- View where each item is being stored
- Claim an item by entering your name — the item is immediately marked as claimed so no one else attempts to pick it up
- Claimed items are visually distinguished and show a disabled "Already Claimed" button

**Admin Dashboard (`/admin`)**
- Password-protected login
- Log new found items with a name, description, and storage location
- View all inventory in a sortable, filterable table (All / Available / Claimed, Newest / Oldest)
- See who claimed each item and when it was added
- Undo a claim if a student checked and the item wasn't theirs
- Remove items from the database once they have been physically picked up

**Security**
- Admin session required to add, remove, or unclaim items
- Cryptographically random secret key generated on first run and persisted locally
- Profanity filter on the claim name field (client-side and server-side)

---

## Frontend Technologies

| Technology | Purpose |
|---|---|
| HTML5 | Page structure and templates |
| CSS3 | Styling, layout, responsive design |
| Vanilla JavaScript | Dynamic rendering, API calls, filtering/sorting |
| [Font Awesome 6](https://fontawesome.com/) | Icons |
| [Google Fonts](https://fonts.google.com/) (Inter, Merriweather) | Typography |
| Jinja2 | Server-side HTML templating (via Flask) |

---

## Backend Technologies

| Technology | Purpose |
|---|---|
| Python 3 | Application logic |
| Flask | Web framework and routing |
| Flask Sessions | Admin authentication |
| Python `secrets` module | Secure key generation |
| Python `json` module | Reading and writing data |
| Gunicorn | Production WSGI server |

---

## Data Storage

There is no external database. All item data is stored in a local `data.json` file in the project root. Each item is a JSON object with the following fields:

```json
{
    "id": 1,
    "name": "AirPods",
    "description": "Apple, white case",
    "location": "Front Desk Bin A",
    "status": "Claimed",
    "date_added": "2026-05-13",
    "claimer_name": "Jane Smith"
}
```

`status` is either `"Found"` (available) or `"Claimed"`. This approach keeps the project dependency-free and easy to back up or reset.

---

## Tech Stack Overview

```
Browser  →  Flask (Python)  →  data.json
              ↓
         Jinja2 Templates
         (index.html, admin.html)
```

- The frontend communicates with Flask via a simple REST API (`/api/items`)
- Flask reads and writes `data.json` on every request
- Admin authentication is handled via server-side sessions
- All UI updates after actions (add, claim, remove) are done without page reloads using `fetch()`

---

## Language & Framework Justification

**Python / Flask** was chosen because it has a minimal setup overhead, is easy to read and modify, and is well-suited to small internal tools that don't require a full framework like Django. For a school project with a single data file and a handful of routes, Flask provides exactly what's needed without unnecessary complexity.

**Vanilla JavaScript** was chosen over a framework like React because the UI interactions are straightforward (fetch data, render HTML, handle clicks) and adding a build step would be unnecessary overhead for a project of this scope.

**JSON file storage** was chosen over a database like SQLite because the dataset is small, the school environment doesn't require concurrent writes at scale, and it keeps the project installable with a single command.

---

## Installation

**Requirements:** Python 3.8 or higher

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Lost-And-Found.git
   cd Lost-And-Found
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open your browser to `http://localhost:5000`

---

## Setup & Configuration

**Admin password:** The admin password is set directly in `app.py` on the line:
```python
if password == 'chargers2026':
```
Change this string to set a new password.

**Secret key:** On first run, a secure random key is automatically generated and saved to `.secret_key` in the project root. This file is git-ignored and should not be shared or committed.

**Data file:** `data.json` is created automatically when the first item is added. To reset the database, delete or clear this file.

---

## Usage

**Students:**
1. Go to the home page and search for your item by name or description
2. If you find it, click **Claim Item** and enter your name
3. Visit the storage location shown on the card to pick it up

**Staff / Admin:**
1. Go to `/admin` and log in with the admin password
2. Use the **Log New Item** form to add found items
3. Use the inventory table to monitor status — filter by Available or Claimed, sort by date
4. Click **Undo Claim** if a student checked and the item wasn't theirs
5. Click **Remove** once an item has been physically picked up

---

## Project Structure

```
Lost-And-Found/
├── app.py              # Flask application, routes, and API
├── data.json           # Item database (auto-created)
├── requirements.txt    # Python dependencies
├── .secret_key         # Auto-generated session key (git-ignored)
├── .gitignore
├── static/
│   └── style.css       # All styling
└── templates/
    ├── index.html      # Student search page
    └── admin.html      # Admin dashboard
```

---

## Challenges Encountered

- **Claim collisions:** Without any lock on the claim action, two students could theoretically claim the same item simultaneously before either saw the updated status. 
- **Input abuse:** An open name field on the claim modal meant students could enter anything, including offensive text.
- **Session security:** Flask's default secret key setup encourages hardcoding a key in source, which would be a security risk if the code is public.
- **Admin API exposure:** The item creation endpoint was initially unprotected, meaning anyone who inspected network requests could add fake items without logging in.
- **Table usability at scale:** As inventory grows, a flat unsorted table becomes hard to manage quickly.

---

## Solutions Implemented

- **Optimistic UI lock:** The "Claim Item" button is replaced with a greyed-out "Already Claimed" button immediately after any claim, reducing (though not eliminating) the collision window.
- **Profanity filter:** Name input is checked against a blocklist both on the client (instant feedback) and server (bypass-proof), stripping non-letter characters before comparison to catch basic obfuscation.
- **Auto-generated secret key:** On first run, `secrets.token_hex(32)` generates a cryptographically secure key saved to `.secret_key`, which is git-ignored so it never enters version control.
- **Admin-gated POST endpoint:** The item creation API now returns 403 if no admin session is present.
- **Filter and sort controls:** The admin inventory table has one-click filters (All / Available / Claimed with live counts) and a Newest/Oldest sort toggle.

---

## Future Improvements

- **Email or notification system** — alert a student when their claimed item is ready, or flag staff when something has been sitting unclaimed for too long
- **Item photos** — allow staff to upload a photo when logging an item so students can visually confirm it's theirs before coming in
- **Student ID field on claims** — replace or supplement the name field with a student ID number for more reliable identification
- **Proper database** — migrate from `data.json` to SQLite or PostgreSQL to support concurrent writes and enable features like search history or audit logs
- **Rate limiting** — prevent a single user from spamming the claim endpoint
- **Expiration / archiving** — automatically flag or archive items that have been sitting in the system for more than 30 days
