# Fledge Enterprises - Courier Dashboard

## Overview
A consignment tracking dashboard for Fledge Enterprises that tracks shipments from Professional Courier and Franch Express services. The application allows uploading Excel files with consignment data, tracking delivery status, and generating email reports.

## Architecture
- **Frontend**: React.js with Tailwind CSS (via CDN), runs on port 5000
- **Backend**: Flask API with SQLite database, runs on port 8000
- **Database**: SQLite stored in `instance/sqlite3.db`

## Project Structure
```
frontend/           # React frontend
  src/
    App.js         # Main React components and pages
    components/    # Sidebar and other components
  public/          # Static assets
app.py             # Flask backend server
models.py          # Database models (Consignment, TrackingHistory, FranchExpress)
processor.py       # Excel processing for Professional Courier
process_excel_fe.py # Excel processing for Franch Express
tracker.py         # Web scraping for Professional Courier tracking
tracker_franch.py  # API calls for Franch Express tracking
uploads/           # Uploaded Excel files storage
```

## Running the Application
The application runs both frontend and backend via `start.sh`:
- Frontend: React dev server on port 5000
- Backend: Flask API on port 8000

The frontend proxies API requests to the backend.

## Environment Variables
Optional email notification configuration:
- `EMAIL_FROM`: Sender email address
- `EMAIL_PASS`: Email password/app password
- `EMAIL_TO`: Recipient email address

## Features
- Upload Excel files with consignment data
- Real-time tracking from courier APIs
- Filter by delivered/pending status
- Search by consignment number or consignee name
- Manual email report generation
- Automatic daily email reports at 9 AM IST
