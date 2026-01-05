import firebase_admin
from firebase_admin import credentials, db
import openpyxl
import schedule
import time
from datetime import datetime

# Firebase setup
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://biopower-a5e93-default-rtdb.firebaseio.com/'
})

def export_firebase_to_excel():
    ref = db.reference("chat_users")
    data = ref.get()

    if not data:
        print("No data to export.")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"

    headers = ["Name", "Contact", "Email", "Amount", "Machine Type", "Company", "Timestamp"]
    ws.append(headers)

    for user_id, user_data in data.items():
        row = [
            user_data.get("name", ""),
            user_data.get("contact", ""),
            user_data.get("email", ""),
            user_data.get("amount_of_waste", ""),
            user_data.get("machine_type", ""),
            user_data.get("company", ""),
            user_data.get("timestamp", "")
        ]
        ws.append(row)

    filename = f"user_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)
    print(f"Exported to {filename}")

# Schedule it to run every hour
schedule.every(1).hour.do(export_firebase_to_excel)

print("Scheduler started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)
