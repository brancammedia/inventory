# CLAUDE.md - Portor Inventory System

## Project Overview
Real-time inventory dashboard for Portor Lighting that displays stock levels across 5 warehouse locations. Data is pulled daily from a Google Sheet and displayed on a static GitHub Pages site with search, filtering, and sorting.

## Tech Stack
- **Frontend**: Single-page HTML with vanilla JavaScript, inline CSS
- **Data**: JSON file (`inventory_data.json`) fetched at runtime
- **Backend**: Python script for data extraction (runs in GitHub Actions)
- **Hosting**: GitHub Pages (static site)
- **Automation**: GitHub Actions scheduled workflow

## File Structure
```
inventory/
├── index.html              # Main dashboard UI (search, filters, table)
├── inventory_data.json     # Auto-generated inventory data
├── update_inventory.py     # Python script - fetches from Google Sheets
├── README.md               # Setup/config documentation
└── .github/workflows/
    └── update-inventory.yml  # Scheduled GitHub Action (7:30 AM EST)
```

## Data Sources
- **Google Sheet**: `1AaWJw1UUxlNmU1QjAleMNLg5JvqS_pp5J0qav1HhZEQ`
  - Tab GID: `618370816` (Inventory List)
  - Must be set to "Anyone with link can view"
  - Exports as CSV via public URL

### Sheet Structure
| Column | Data |
|--------|------|
| A | Category/Subcategory |
| B | SKU |
| C | Description |
| D | Wattage |
| E-I | Warehouse quantities (Ontario, Louisville, Phoenix, Dallas, Chicago) |
| J | Total |
| K | Notes |

## Build/Deploy Process
1. **Scheduled**: GitHub Action runs daily at 7:30 AM EST (cron: `30 12 * * *`)
2. **Manual**: Actions tab > "Update Inventory Data" > "Run workflow"
3. Python script fetches CSV from Google Sheets, parses to JSON
4. Commits `inventory_data.json` if changed
5. GitHub Pages auto-deploys on commit

### Verify Schedule is Working
```bash
gh api repos/brancammedia/inventory/actions/runs?per_page=1 --jq '.workflow_runs[0] | "\(.event) | \(.created_at)"'
```
- Should show `schedule` event type (not just `workflow_dispatch`)

## Current State
**Working:**
- Dashboard displays 700+ SKUs with quantities per warehouse
- Search by SKU/description
- Filter by category
- Location tabs filter by warehouse
- Mobile responsive
- Full EST timestamp (date + time) matching pricing portal

**Timestamp Format:**
- Display: `"January 24, 2026 at 07:30 AM EST"`
- Updated in both header subtitle and badge
- Schedule re-enabled January 2026

**Known Issues:**
- Scheduled workflows may stop if repo inactive 60+ days
- If schedule stops working, push a small change to `.github/workflows/update-inventory.yml` to re-register

**Future/In Progress:**
- Clearance and Closeout tabs (GIDs commented out in `update_inventory.py`)

## Common Tasks

### Trigger manual update
```bash
gh workflow run update-inventory.yml --repo brancammedia/inventory
```

### Check last update timestamp
```bash
gh api repos/brancammedia/inventory/contents/inventory_data.json --jq '.content' | base64 -d | head -3
```

### Add new category mapping
Edit `CATEGORY_MAP` dict in `update_inventory.py` to normalize category names

### Change update schedule
Edit cron in `.github/workflows/update-inventory.yml` (use UTC time)

### Debug data parsing
Run locally: `python update_inventory.py` - outputs to `inventory_data.json`

---
*Last updated: January 24, 2026*
