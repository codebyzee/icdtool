from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__, template_folder="templates")

# Update the database path to the new merged database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "merged_cdps_medicaid.db")

if not os.path.exists(db_path):
    print(f"❌ Error: Database file '{db_path}' not found!")
    exit(1)

def search_icd10(query):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Parameterized query to avoid SQL injection
        query_param = f"%{query}%"
        cursor.execute("""
            SELECT ICD10_Code, Condition, Chronic, Medicaid_Guideline_Summary
            FROM merged_icd10
            WHERE ICD10_Code LIKE ? OR Condition LIKE ?
            LIMIT 10
        """, (query_param, query_param))

        results = cursor.fetchall()
        conn.close()

        # Return results as a list of dictionaries
        return [
            {
                "ICD10_Code": row[0],
                "Condition": row[1],
                "Chronic": row[2],
                "Medicaid_Guideline_Summary": row[3]
            }
            for row in results
        ]
    except sqlite3.Error as e:
        print(f"❌ Database Error: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])  # Return an empty list if query is empty
    results = search_icd10(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)