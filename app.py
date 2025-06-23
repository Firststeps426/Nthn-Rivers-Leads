#!/usr/bin/env python3
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import datetime
import requests
from bs4 import BeautifulSoup
import time
import threading
import json

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    
    # Create leads table
    c.execute('''CREATE TABLE IF NOT EXISTS leads
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  location TEXT NOT NULL,
                  source TEXT NOT NULL,
                  contact_info TEXT,
                  budget_range TEXT,
                  property_type TEXT,
                  score INTEGER,
                  status TEXT DEFAULT 'new',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create search_locations table
    c.execute('''CREATE TABLE IF NOT EXISTS search_locations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  location_name TEXT NOT NULL,
                  postcode TEXT,
                  state TEXT,
                  active INTEGER DEFAULT 1,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insert sample Northern Rivers leads
    sample_leads = [
        ("Acreage maintenance needed - 5 acres Bangalow", "Bangalow, NSW 2481", "Facebook - Byron Bay Community Board", "Contact via Facebook group", "$1,200-1,800/month", "Acreage", 92),
        ("Tree removal and cleanup - Federal property", "Federal, NSW 2480", "Gumtree Northern Rivers", "Phone: 0412 345 678", "$2,000-3,000 one-off", "Rural Property", 88),
        ("Garden renovation for new waterfront home", "Byron Bay, NSW 2481", "Facebook Marketplace", "Email: sarah.m@email.com", "$25,000-40,000", "Waterfront", 95),
        ("Rural property maintenance - Mullumbimby", "Mullumbimby, NSW 2482", "Local Community Board", "Contact: 0423 567 890", "$800-1,200/month", "Rural Block", 90),
        ("Landscaping for new build - Ballina", "Ballina, NSW 2478", "Council DA Applications", "Developer: ABC Constructions", "$15,000-25,000", "New Build", 87),
        ("Lifestyle block setup - Nimbin", "Nimbin, NSW 2480", "Instagram - #nimbinlife", "DM @greenthumb_nimbin", "$5,000-8,000", "Lifestyle Block", 85),
        ("Commercial grounds maintenance - Lismore", "Lismore, NSW 2480", "Tender Website", "Email: facilities@company.com.au", "$2,500/month ongoing", "Commercial", 91),
        ("Storm damage cleanup - Casino", "Casino, NSW 2470", "Airtasker", "Via Airtasker platform", "$3,000-5,000", "Storm Damage", 89)
    ]
    
    # Insert sample locations
    sample_locations = [
        ("Byron Bay", "2481", "NSW"),
        ("Bangalow", "2479", "NSW"),
        ("Mullumbimby", "2482", "NSW"),
        ("Federal", "2480", "NSW"),
        ("Nimbin", "2480", "NSW"),
        ("Lismore", "2480", "NSW"),
        ("Ballina", "2478", "NSW"),
        ("Casino", "2470", "NSW")
    ]
    
    for lead in sample_leads:
        c.execute("""INSERT OR IGNORE INTO leads 
                     (title, location, source, contact_info, budget_range, property_type, score) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", lead)
    
    for location in sample_locations:
        c.execute("INSERT OR IGNORE INTO search_locations (location_name, postcode, state) VALUES (?, ?, ?)", location)
    
    conn.commit()
    conn.close()

# Lead collection functions
def collect_leads_from_sources(location="Northern Rivers"):
    """Simulate lead collection from various sources"""
    # In a real implementation, this would scrape actual websites
    # For demo purposes, we'll simulate finding new leads
    
    sources = [
        "Facebook - Byron Bay Community",
        "Gumtree Northern Rivers", 
        "Council DA Applications",
        "Airtasker",
        "Local Classifieds",
        "Instagram Local Tags"
    ]
    
    # Simulate finding 1-3 new leads
    import random
    new_leads = []
    
    if random.random() > 0.7:  # 30% chance of finding new leads
        num_leads = random.randint(1, 2)
        for i in range(num_leads):
            lead = {
                'title': f"New {random.choice(['landscaping', 'maintenance', 'cleanup'])} project - {location}",
                'location': f"{location}, NSW",
                'source': random.choice(sources),
                'score': random.randint(75, 95),
                'contact_info': "Contact details available",
                'budget_range': f"${random.randint(500, 5000)}-{random.randint(5000, 15000)}",
                'property_type': random.choice(['Residential', 'Commercial', 'Acreage', 'Rural'])
            }
            new_leads.append(lead)
    
    return new_leads

def background_lead_collection():
    """Background thread for continuous lead collection"""
    while True:
        try:
            # Get active search locations
            conn = sqlite3.connect('leads.db')
            c = conn.cursor()
            c.execute("SELECT location_name FROM search_locations WHERE active = 1")
            locations = [row[0] for row in c.fetchall()]
            conn.close()
            
            # Collect leads for each location
            for location in locations:
                new_leads = collect_leads_from_sources(location)
                
                if new_leads:
                    conn = sqlite3.connect('leads.db')
                    c = conn.cursor()
                    
                    for lead in new_leads:
                        c.execute("""INSERT INTO leads 
                                     (title, location, source, contact_info, budget_range, property_type, score) 
                                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                 (lead['title'], lead['location'], lead['source'], 
                                  lead['contact_info'], lead['budget_range'], lead['property_type'], lead['score']))
                    
                    conn.commit()
                    conn.close()
                    print(f"Added {len(new_leads)} new leads for {location}")
            
            # Wait 15 minutes before next collection
            time.sleep(900)  # 15 minutes
            
        except Exception as e:
            print(f"Error in lead collection: {e}")
            time.sleep(300)  # Wait 5 minutes on error

# Routes
@app.route('/')
def dashboard():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    
    # Get recent leads
    c.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 20")
    recent_leads = c.fetchall()
    
    # Get statistics
    c.execute("SELECT COUNT(*) FROM leads")
    total_leads = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM leads WHERE score >= 90")
    high_priority = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_at) = DATE('now')")
    today_leads = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT location) FROM leads")
    locations_covered = c.fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html', 
                         leads=recent_leads,
                         total_leads=total_leads,
                         high_priority=high_priority,
                         today_leads=today_leads,
                         locations_covered=locations_covered)

@app.route('/search_location', methods=['POST'])
def search_location():
    location = request.form.get('location', '').strip()
    
    if location:
        # Add to search locations
        conn = sqlite3.connect('leads.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO search_locations (location_name, active) VALUES (?, 1)", (location,))
        conn.commit()
        conn.close()
        
        # Immediately search for leads in this location
        new_leads = collect_leads_from_sources(location)
        
        if new_leads:
            conn = sqlite3.connect('leads.db')
            c = conn.cursor()
            
            for lead in new_leads:
                c.execute("""INSERT INTO leads 
                             (title, location, source, contact_info, budget_range, property_type, score) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (lead['title'], lead['location'], lead['source'], 
                          lead['contact_info'], lead['budget_range'], lead['property_type'], lead['score']))
            
            conn.commit()
            conn.close()
    
    return redirect(url_for('dashboard'))

@app.route('/leads')
def leads():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    
    # Get filter parameters
    source_filter = request.args.get('source', '')
    score_filter = request.args.get('min_score', 0, type=int)
    
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    
    if source_filter:
        query += " AND source LIKE ?"
        params.append(f"%{source_filter}%")
    
    if score_filter:
        query += " AND score >= ?"
        params.append(score_filter)
    
    query += " ORDER BY score DESC, created_at DESC"
    
    c.execute(query, params)
    leads = c.fetchall()
    
    # Get unique sources for filter dropdown
    c.execute("SELECT DISTINCT source FROM leads ORDER BY source")
    sources = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    return render_template('leads.html', leads=leads, sources=sources)

@app.route('/api/leads')
def api_leads():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY created_at DESC LIMIT 50")
    leads = c.fetchall()
    conn.close()
    
    leads_data = []
    for lead in leads:
        leads_data.append({
            'id': lead[0],
            'title': lead[1],
            'location': lead[2],
            'source': lead[3],
            'contact_info': lead[4],
            'budget_range': lead[5],
            'property_type': lead[6],
            'score': lead[7],
            'status': lead[8],
            'created_at': lead[9]
        })
    
    return jsonify(leads_data)

if __name__ == '__main__':
    init_db()
    
    # Start background lead collection in production
    if os.environ.get('FLASK_ENV') != 'development':
        collection_thread = threading.Thread(target=background_lead_collection, daemon=True)
        collection_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

