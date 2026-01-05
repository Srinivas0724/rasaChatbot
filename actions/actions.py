from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from rasa_sdk.events import EventType
import datetime
import firebase_admin
from firebase_admin import credentials, db

# Firebase Initialization (run only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-adminsdk.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://biopower-6c909-default-rtdb.firebaseio.com'
    })

class ActionHandleWetWasteInfo(Action):
    def name(self) -> str:
        return "action_handle_wet_waste_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        waste_amount = tracker.get_slot("waste_amount")

        if waste_amount is None:
            dispatcher.utter_message(text="❌ I didn't receive the amount of waste. Please enter it in kilograms.")
            return []

        try:
            waste_amount = float(waste_amount)
        except ValueError:
            dispatcher.utter_message(text="❌ Please provide a valid number for waste amount.")
            return []

        if waste_amount <= 0:
            dispatcher.utter_message(text="⚠️ Please enter a valid amount of waste (greater than 0 kg).")
            return []

        if 1 <= waste_amount <= 49:
            category = "🏡 Domestic Waste"
            info = (
                f"{category}:\n"
                "This includes household kitchen waste, fruit/vegetable peels, etc.\n"
                "👉 Recommended solution: Small Organic Converter Units or Bio Composting Bins."
            )
        elif 50 <= waste_amount <= 4999:
            category = "🏭 Institutional & Small Industrial Waste"
            info = (
                f"{category}:\n"
                "Waste from hotels, schools, apartments, and small-scale industries.\n"
                "👉 Recommended solution: Medium-scale Bio Gas Plant or Organic Converter."
            )
        else:
            category = "⛽ CNG-Level Waste"
            info = (
                f"{category}:\n"
                "Large-scale organic waste suitable for bio-CNG generation and industrial composting.\n"
                "👉 Recommended solution: Industrial-scale Bio Gas or CNG Plant Setup."
            )

        dispatcher.utter_message(text=info)
        return []



class ActionSaveUnhandledMessage(Action):
    def name(self):
        return "action_save_unhandled_message"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):

        # Get the last user message
        user_message = tracker.latest_message.get("text")
        intent_name = tracker.latest_message.get("intent", {}).get("name")

        # Only save if it's actually unrecognized
        if intent_name == "nlu_fallback" or intent_name == "None":
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            data = {
                "message": user_message,
                "timestamp": timestamp
            }

            # Save to Firebase under /unhandled_messages
            ref = db.reference('unhandled_messages')
            ref.push().set(data)

            # Send fallback message to UI
            dispatcher.utter_message(text="Sorry, we don't understand it. Please tell us more.")
        return []
class ActionSaveUserMessage(Action):
    def name(self) -> str:
        return "action_save_user_message"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> List[EventType]:

        user_message = tracker.latest_message.get('text')
        print(f"📥 User message received: {user_message}")

         # Save to Firebase
        ref = db.reference('user_messages')
        ref.push().set({
            'message': user_message,
            'timestamp': str(tracker.latest_message.get('timestamp'))
        })
        return []
    

class ActionHandleWasteAmount(Action):
    def name(self) -> str:
        return "action_handle_waste_amount"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict) -> List[EventType]:

        # Get the user message text (waste amount input)
        user_message = tracker.latest_message.get("text")
        
        # TODO: Implement waste amount handling logic
        dispatcher.utter_message(text="Waste amount handling not yet implemented.")
        
        return []



class ActionCheckComposterAvailability(Action):
    def name(self) -> str:
        return "action_check_composter_availability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):

        waste_amount = tracker.get_slot("waste_amount")

        if waste_amount is None:
            dispatcher.utter_message(text="⚠️ Please enter the waste amount first.")
            return []

        if int(waste_amount) < 50:
            dispatcher.utter_message(text="<b>⚠️ The entered waste amount is below the average required for OWC processing.</b><br><br> <b>📞 Please contact our technical team for further assistance.</b><br><br> - Contact details : +91 7338129464 / +91 9686623587" )
        else:
            dispatcher.utter_message(text="✅ OWC machine is suitable for your waste amount. Proceeding with Composter.")

        return []