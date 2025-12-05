#!/usr/bin/env python3
"""
Script to view patient records and conversation history from the database
"""
import sqlite3
from datetime import datetime


def view_all_patients():
    """Display all patient records"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM patients ORDER BY created_at DESC')
    patients = cursor.fetchall()

    print("=" * 80)
    print("PATIENT RECORDS")
    print("=" * 80)
    print()

    if not patients:
        print("No patient records found.")
        conn.close()
        return

    for patient in patients:
        patient_id, conv_id, name, age, location, problem, created_at = patient
        print(f"ID: {patient_id}")
        print(f"Conversation ID: {conv_id}")
        print(f"Name: {name}")
        print(f"Age: {age}")
        print(f"Location: {location}")
        print(f"Problem: {problem}")
        print(f"Created: {created_at}")
        print("-" * 80)

    conn.close()


def view_conversation_history(conversation_id=None):
    """Display conversation history"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()

    print()
    print("=" * 80)
    print("CONVERSATION HISTORY")
    print("=" * 80)
    print()

    if conversation_id:
        cursor.execute('''
            SELECT * FROM conversation_history
            WHERE conversation_id = ?
            ORDER BY question_index
        ''', (conversation_id,))
    else:
        cursor.execute('''
            SELECT * FROM conversation_history
            ORDER BY created_at DESC
        ''')

    conversations = cursor.fetchall()

    if not conversations:
        print("No conversation history found.")
        conn.close()
        return

    current_conv = None
    for conv in conversations:
        conv_id, c_id, question, answer, q_index, created_at = conv

        if c_id != current_conv:
            if current_conv is not None:
                print("-" * 80)
            print(f"\nConversation: {c_id}")
            print(f"Time: {created_at}")
            print()
            current_conv = c_id

        print(f"Q{q_index + 1}: {question}")
        print(f"A{q_index + 1}: {answer}")
        print()

    conn.close()


def view_latest_patient():
    """Display the most recent patient record with full conversation"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM patients ORDER BY created_at DESC LIMIT 1')
    patient = cursor.fetchone()

    if not patient:
        print("No patient records found.")
        conn.close()
        return

    patient_id, conv_id, name, age, location, problem, created_at = patient

    print("=" * 80)
    print("LATEST PATIENT RECORD")
    print("=" * 80)
    print()
    print(f"Name: {name}")
    print(f"Age: {age}")
    print(f"Location: {location}")
    print(f"Problem: {problem}")
    print(f"Recorded: {created_at}")
    print()
    print("Full Conversation:")
    print("-" * 80)

    cursor.execute('''
        SELECT question, answer, question_index
        FROM conversation_history
        WHERE conversation_id = ?
        ORDER BY question_index
    ''', (conv_id,))

    conversations = cursor.fetchall()

    for question, answer, q_index in conversations:
        print(f"\nQ: {question}")
        print(f"A: {answer}")

    print()
    print("=" * 80)

    conn.close()


def get_stats():
    """Display database statistics"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM patients')
    patient_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM conversation_history')
    conversation_count = cursor.fetchone()[0]

    print("=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    print(f"Total Patients: {patient_count}")
    print(f"Total Conversation Entries: {conversation_count}")
    print("=" * 80)
    print()

    conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "latest":
            view_latest_patient()
        elif command == "patients":
            view_all_patients()
        elif command == "conversations":
            view_conversation_history()
        elif command == "stats":
            get_stats()
        else:
            print("Unknown command. Use: latest, patients, conversations, or stats")
    else:
        # Default: show everything
        get_stats()
        view_all_patients()
        view_conversation_history()
