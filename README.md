# Portor Lighting Inventory System

Real-time inventory availability dashboard that automatically updates daily from Google Sheets.

## Features

- **Live Inventory Data**: Pulls from Google Sheets daily at 7:30 AM Pacific
- **5 Warehouse Locations**: Ontario, Louisville, Phoenix, Dallas, Chicago
- **Filtering**: By category, subcategory, and stock level
- **Search**: By SKU, description, or category
- **Sortable Columns**: Click headers to sort
- **Mobile Responsive**: Works on all devices

## Setup

### 1. Google Sheet Permissions

Make sure your inventory Google Sheet is set to **"Anyone with the link can view"**:
1. Open the sheet
2. Click Share
3. Change "General access" to "Anyone with the link"
4. Set to "Viewer"

### 2. Deploy to GitHub Pages

1. Push this repository to GitHub
2. Go to Settings > Pages
3. Set Source to "Deploy from a branch"
4. Select `main` branch and `/ (root)` folder
5. Click Save

Your inventory page will be live at: `https://[username].github.io/[repo-name]/`

### 3. Automatic Updates

The GitHub Action runs automatically at 7:30 AM Pacific every day.

To manually trigger an update:
1. Go to Actions tab
2. Select "Update Inventory Data"
3. Click "Run workflow"

## Files

- `index.html` - The inventory dashboard
- `inventory_data.json` - Current inventory data (auto-updated)
- `update_inventory.py` - Python script that pulls from Google Sheets
- `.github/workflows/update-inventory.yml` - GitHub Action for scheduled updates

## Configuration

### Adding More Sheet Tabs

Edit `update_inventory.py` and add tabs to the `TABS` list:

```python
TABS = [
    ("618370816", "inventory", "Inventory List"),
    ("CLEARANCE_GID", "clearance", "Clearance"),
    ("CLOSEOUT_GID", "closeout", "Closeout"),
]
```

Replace `CLEARANCE_GID` and `CLOSEOUT_GID` with the actual tab GIDs from your Google Sheet URL.

### Changing Update Schedule

Edit `.github/workflows/update-inventory.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '30 15 * * *'  # 7:30 AM Pacific (PST)
```

## Troubleshooting

**Data not loading?**
- Check that the Google Sheet is publicly viewable
- Verify the sheet GID in `update_inventory.py`
- Check GitHub Actions logs for errors

**GitHub Pages not working?**
- Make sure Pages is enabled in repository settings
- Wait a few minutes for deployment

---

© 2026 Portor Lighting
