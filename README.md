# Campus Lost and Found

A web based system for campus students to report lost items, report found items, search for items, and claim their belongings in one place.

Instead of posting in WhatsApp groups or putting paper notices on walls, students can now report and find items online.

Live Demo: https://zaheerullah1.pythonanywhere.com

## Features

- Login with Name and Roll Number
- Report Lost Item name, category, location, date and description
- Report Found Item so the owner can find it
- Search and browse all lost and found items
- Dashboard to see total Lost, Found, Claimed and Pending items
- Claim System to claim an item if it is yours
- Works on mobile and laptop browser

## Tech Stack Used

- Language: Python 3
- Backend Framework: Flask
- Database: SQLite, file lost_found.db is auto created
- Frontend: HTML rendered directly inside app.py, no separate CSS or Bootstrap file
- Charts Logic: Python in charts.py
- Server for Deployment: Gunicorn
- Hosting: Render Free Plan

## Project Files

- app.py - Main Flask app, all HTML pages and routes
- database.py - SQLite database functions for create, add, search and claim
- utils.py - Helper and validation functions
- charts.py - Dashboard counts and chart data
- requirements.txt - Flask and Gunicorn
- Procfile - Render start command gunicorn app:app
- .gitignore - Ignores db, pycache and logs
- README.md - This file

There is no templates folder and no static folder in this version.

## How To Run Locally

Step 1, go to folder:
cd campus-lost-found

Step 2, install:
pip install -r requirements.txt

Step 3, run:
python app.py

Then open in browser:
http://127.0.0.1:5000

Test Login:
Name: Ahmad Ali
Roll: CS-2023-045

## How To Use

1. Login with your Name and Roll Number
2. Open Dashboard to see all stats
3. Click Report Lost if you lost something
4. Click Report Found if you found something
5. Use Search to find your item
6. Click Claim to claim your item

## How Much Is This App Complete

This is a working MVP, about 60 percent complete.

Done:
- Core Idea, Report Lost and Found, Search and List, Dashboard, Claim System

Partly Done:
- Login is basic with no password, Design is simple, Security is basic

Not Done Yet:
- Image Upload, Notifications, Admin Panel, Proper Password Login

This is enough for FYP Demo, Class Presentation and Viva.

## Future Improvements To Make It Perfect

Phase 2 Must Have:
- Proper Login with Password, Signup and Forgot Password
- Image Upload for photo of lost item
- Separate Frontend with templates folder, style.css and Bootstrap for beautiful UI
- Admin Panel to approve, reject and delete fake reports
- Match System to auto suggest your lost item may match a found item

Phase 3 Advanced:
- Notifications by Email or WhatsApp when your item is found
- QR Claim to verify claim at office
- Categories and Filters like Wallet, ID Card, Mobile, Keys, Bag
- Location Map to show where item was lost on campus
- My Reports page to see all items you reported
- PostgreSQL Database instead of SQLite so data does not delete on Render restart

Phase 4 Perfect App:
- Flutter Mobile App for Android and iOS
- Chat between Owner and Finder inside app
- Reward System with points for returning items
- Multi Campus support for multiple universities

If all this is added, this becomes a 100 percent complete professional product.

## Author

Computer Student Project - Built with Python Flask

## License

Free for educational use.
