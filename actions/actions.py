import string

import psycopg2
from typing import Any, Text, Dict, List, Optional, Tuple
from rasa_sdk import Action, Tracker
import random
from rasa_sdk.executor import CollectingDispatcher


def fetch_from_db(query: str, params: Optional[Tuple] = None) -> List[Tuple]:
    try:
        with psycopg2.connect(
                dbname="chatbot",
                user="simsim",
                password="simsim",
                host="localhost",
                port="5432"
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    except Exception as e:
        raise RuntimeError(f"Erreur base de données : {e}")


def delete_from_db(query: str, params: Optional[Tuple] = None) -> int:
    """
    Exécute une requête DELETE et retourne le nombre de lignes supprimées.
    """
    try:
        with psycopg2.connect(
                dbname="chatbot",
                user="simsim",
                password="simsim",
                host="localhost",
                port="5432"
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                deleted_rows = cursor.rowcount
            conn.commit()
            return deleted_rows
    except Exception as e:
        raise RuntimeError(f"Erreur base de données (delete) : {e}")


def insert_into_db(query: str, params: Tuple[Any, ...]) -> None:
    import psycopg2
    try:
        with psycopg2.connect(
                dbname="chatbot",
                user="simsim",
                password="simsim",
                host="localhost",
                port="5432"
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
            conn.commit()
    except Exception as e:
        raise RuntimeError(f"Erreur base de données (insert) : {e}")


def generate_booking_code(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_uppercase, k=length))


class ActionShowDailyMenu(Action):
    def name(self) -> Text:
        return "action_show_daily_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            rows = fetch_from_db("SELECT plat, allergens FROM daily_menu")

            if not rows:
                dispatcher.utter_message(text="Le menu du jour n'est pas encore disponible.")
            else:
                message = "📋 Menu du jour :\n"
                for plat, allergenes in rows:
                    message += f"- {plat} (Allergènes : {allergenes})\n"
                dispatcher.utter_message(text=message)

        except RuntimeError as e:
            dispatcher.utter_message(text=str(e))

        return []


class ActionShowFullMenu(Action):
    def name(self) -> Text:
        return "action_show_dish_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            rows = fetch_from_db("""
                                 SELECT p.name,
                                        p.description,
                                        p.price,
                                        COALESCE(STRING_AGG(a.name, ', '), 'aucun')
                                 FROM plats p
                                          LEFT JOIN plat_allergen pa ON p.id = pa.plat_id
                                          LEFT JOIN allergens a ON pa.allergen_id = a.id
                                 GROUP BY p.id
                                 """)

            if not rows:
                dispatcher.utter_message(text="La carte est vide pour l'instant.")
            else:
                message = "📋 Voici la carte complète :\n\n"
                for nom, description, prix, allergenes in rows:
                    message += f"🍽️ {nom} - {prix:.2f} €\n"
                    message += f"   {description}\n"
                    message += f"   Allergènes : {allergenes}\n\n"
                dispatcher.utter_message(text=message)

        except RuntimeError as e:
            dispatcher.utter_message(text=str(e))

        return []


class ActionCancelBookingNumber(Action):
    def name(self) -> Text:
        return "action_cancel_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        booking_number = tracker.get_slot("booking_number")
        print(booking_number)

        if not booking_number:
            dispatcher.utter_message(text="Je n'ai pas compris votre numéro de réservation.")
            return []

        try:
            deleted = delete_from_db(
                "DELETE FROM bookings WHERE code = %s",
                (booking_number,)
            )

            if deleted > 0:
                dispatcher.utter_message(text=f"La réservation {booking_number} a bien été annulée.")
                print(f"🗑️ Réservation supprimée : {booking_number}")
            else:
                dispatcher.utter_message(text=f"Aucune réservation trouvée pour le numéro {booking_number}.")

        except Exception as e:
            dispatcher.utter_message(text=f"Erreur lors de l'annulation : {e}")
            print(f"❌ Erreur SQL : {e}")

        return []


class ActionBookTable(Action):
    def name(self) -> Text:
        return "action_book_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        time = tracker.get_slot("time")
        number_of_people = tracker.get_slot("number_of_people")
        phone = tracker.get_slot("phone")

        if not time or not number_of_people:
            dispatcher.utter_message(text="Certaines informations sont manquantes pour réserver.")
            return []

        try:
            booking_code = generate_booking_code()

            insert_into_db("""
                           INSERT INTO bookings (phone, guest_count, reservation_date, code)
                           VALUES (%s, %s, %s, %s)
                           """, (
                               phone or "inconnu",
                               number_of_people,
                               time,
                               booking_code
                           ))

            dispatcher.utter_message(text=(
                f"✅ Réservation enregistrée !\n\n"
                f"📅 Date : {time}\n"
                f"👥 Nombre de personnes : {number_of_people}\n"
                f"📞 Téléphone : {phone or 'non renseigné'}\n"
                f"🔐 Code de réservation : {booking_code}"
            ))

        except RuntimeError as e:
            dispatcher.utter_message(text=str(e))

        return []


class ActionGetBookings(Action):
    def name(self) -> Text:
        return "action_get_bookings"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        phone = tracker.get_slot("phone")  # On récupère le slot 'phone' de l'utilisateur

        if not phone:
            dispatcher.utter_message(text="Je n'ai pas compris votre numéro de téléphone.")
            return []

        try:
            # Interrogation de la base de données pour récupérer les réservations par téléphone
            rows = fetch_from_db("""
                                 SELECT code, guest_count, reservation_date
                                 FROM bookings
                                 WHERE phone = %s
                                 """, (phone,))

            if not rows:
                dispatcher.utter_message(text=f"Aucune réservation trouvée pour le numéro {phone}.")
            else:
                message = f"Voici les réservations associées au numéro {phone} :\n"
                for code, guest_count, reservation_date in rows:
                    message += f"Réservation {code} : {guest_count} personnes, le {reservation_date}\n"
                dispatcher.utter_message(text=message)

        except RuntimeError as e:
            dispatcher.utter_message(text=f"Erreur lors de la récupération des réservations : {e}")
            print(f"❌ Erreur SQL : {e}")

        return []
