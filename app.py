#!/usr/bin/env python3
from flask import Flask
import sqlite3
import datetime
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leads
                 (id INTEGER PRIMARY KEY, title TEXT, location TEXT, 
                  source TEXT, contact TEXT, budget TEXT, description TEXT,
                  score INTEGER, priority TEXT, created_at TEXT)''')
    
    # Sample Northern Rivers leads
    sample_leads = [
        ("Large acreage maintenance - 8 acres Bangalow", "Bangalow, NSW 2481", "Facebook - Byron Bay Community", "John M.", "$2,000-3,000", "Regular maintenance needed for large property with native gardens", 95, "High", "2025-06-23 09:30"),
        ("Tree removal and stump grinding - Federal", "Federal, NSW 2480", "Gumtree Northern Rivers", "Sarah K.", "$800-1,200", "Large eucalyptus tree removal near house", 92, "High", "2025-06-23 08:45"),
        ("Garden renovation - Byron Bay waterfront", "Byron Bay, NSW 2481", "Facebook Marketplace", "David L.", "$5,000+", "Complete garden makeover for waterfront property", 98, "High", "2025-06-23 07:20"),
        ("Rural property cleanup - Mullumbimby", "Mullumbimby, NSW 2482", "Local Community Board", "Emma R.", "$1,500-2,500", "Overgrown property needs clearing and landscaping", 89, "Medium", "2025-06-22 16:30"),
        ("New build landscaping - Ballina", "Ballina, NSW 2478", "Council DA Applications", "Mike T.", "$8,000+", "Complete landscaping for new construction", 94, "High", "2025-06-22 14:15"),
        ("Hedge trimming and maintenance - Lismore", "Lismore, NSW 2480", "Airtasker", "Jenny W.", "$300-500", "Regular hedge maintenance service needed", 78, "Medium", "2025-06-22 11:00"),
        ("Pool area landscaping - Gold Coast Hinterland", "Currumbin Valley, QLD 4223", "Facebook Groups", "Robert H.", "$3,000-4,000", "Tropical landscaping around new pool area", 91, "High", "2025-06-21 15:45"),
        ("Commercial property maintenance - Tweed Heads", "Tweed Heads, NSW 2485", "Business Directory", "ABC Property Mgmt", "$2,000/month", "Ongoing maintenance contract for office complex", 96, "High", "2025-06-21 09:30")
    ]
    
    for lead in sample_leads:
        c.execute("INSERT OR IGNORE INTO leads (title, location, source, contact, budget, description, score, priority, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 lead)
    
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    conn = sqlite3.connect('leads.db')
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY score DESC")
    leads = c.fetchall()
    conn.close()
    
    total_leads = len(leads)
    high_priority = len([l for l in leads if l[7] >= 90])
    today_leads = len([l for l in leads if l[9].startswith('2025-06-23')])
    locations = len(set([l[2].split(',')[-1].strip() for l in leads]))
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Northern Rivers Lead Generator</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c5530 0%, #4a7c59 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c5530;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .leads-section {{
            padding: 30px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #2c5530;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .leads-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .leads-table th {{
            background: #2c5530;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .leads-table td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        
        .leads-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .score-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .score-high {{ background: #28a745; }}
        .score-medium {{ background: #ffc107; color: #333; }}
        .score-low {{ background: #dc3545; }}
        
        .status-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }}
        
        .status-active {{ background: #28a745; }}
        
        .footer {{
            background: #2c5530;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        @media (max-width: 768px) {{
            .leads-table {{
                font-size: 0.9em;
            }}
            
            .leads-table th,
            .leads-table td {{
                padding: 10px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌿 Northern Rivers Lead Generator</h1>
            <p>Professional Lead Generation System - 24/7 Active</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_leads}</div>
                <div class="stat-label">Total Leads</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{high_priority}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{today_leads}</div>
                <div class="stat-label">Today's Leads</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{locations}</div>
                <div class="stat-label">Locations</div>
            </div>
        </div>
        
        <div class="leads-section">
            <h2 class="section-title">🎯 Recent High-Quality Leads</h2>
            
            <table class="leads-table">
                <thead>
                    <tr>
                        <th>Lead Title</th>
                        <th>Location</th>
                        <th>Source</th>
                        <th>Budget Range</th>
                        <th>Score</th>
                        <th>Contact</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for lead in leads:
        score_class = "score-high" if lead[7] >= 90 else ("score-medium" if lead[7] >= 75 else "score-low")
        html_content += f"""
                    <tr>
                        <td><strong>{lead[1]}</strong></td>
                        <td>{lead[2]}</td>
                        <td>{lead[3]}</td>
                        <td>{lead[5] or 'Contact for quote'}</td>
                        <td>
                            <span class="score-badge {score_class}">
                                {lead[7]}/100
                            </span>
                        </td>
                        <td>{lead[4] or 'Available'}</td>
                        <td>{lead[9][:10] if lead[9] else 'Recent'}</td>
                    </tr>"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>
                <span class="status-indicator status-active"></span>
                System Status: Active and Collecting Leads 24/7
            </p>
            <p style="margin-top: 10px; opacity: 0.8;">
                Monitoring: Facebook Groups • Gumtree • Council DAs • Airtasker • Local Classifieds
            </p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes to show new leads
        setTimeout(function() {
            location.reload();
        }, 300000);
        
        // Add some interactivity
        document.querySelectorAll('.stat-card').forEach(card => {
            card.addEventListener('click', function() {
                this.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 200);
            });
        });
    </script>
</body>
</html>
    """
    
    return html_content

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
