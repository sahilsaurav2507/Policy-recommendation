from flask import Flask, jsonify, request, redirect, render_template
from flask_cors import CORS
from flask_bcrypt import Bcrypt

from datetime import datetime
from transformers import pipeline
from google.generativeai import GenerativeModel
import google.generativeai as genai


from datetime import datetime


import mysql.connector
genai.configure(api_key="AIzaSyCGYJm4vvSR7crEOmddYBnibeQSb3AKXkk")

# Create Flask app and specify template folder (pointing directly to frontend)
app = Flask(__name__, template_folder='../frontend')
app.secret_key = "SECRET_KEY"
CORS(app)
bcrypt = Bcrypt(app)

# In-memory flag to track login status
session = {}

# Connect to MySQL database
mycon = mysql.connector.connect(
  host="localhost",
  user="root",
  password="pabbo123",
  database="govt"
)

cur = mycon.cursor()
mycon.autocommit = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['GET', 'POST'])
def register_user():
    if request.method == "POST":
        data = request.get_json()
        
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        user_type = data.get("user_type")
        ministry_name = data.get("ministry_name", None)
        department_name = data.get("department_name", None)
        department_desc = data.get("department_desc", None)
        
        hash_password = bcrypt.generate_password_hash(password, 10).decode('utf-8')
        
        # check if the user with same usernam or email already exists
        cur.execute("SELECT username FROM users WHERE username=%s OR email=%s", (username, email))
        user = cur.fetchall()
        if not user:
            cur.execute("INSERT INTO users (username, email, password_hash, user_type, ministry_name, department_name, department_description) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (username, email, hash_password, user_type, ministry_name, department_name, department_desc))
            cur.execute("SELECT user_id, username, user_type FROM users WHERE username=%s OR email=%s", (username, email))
            user = cur.fetchall()
            # session['user_id'] = user[0][0]
            # session['username'] = user[0][1]
            
            return jsonify({"message": "Registration successful", "redirect": "/api/login/"}), 200
        else:
            return jsonify({"message": "Username or Email already exists"}), 401

    return jsonify({'message': 'Load Registration page'}), 200

@app.route('/api/login', methods=['GET', 'POST'])
def login_user():
    # if request.method == 'OPTIONS':
    #     response = jsonify()
    #     response.headers['Access-Control-Allow-Methods'] = 'POST'
    #     response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    #     response.headers['Access-Control-Allow-Credentials'] = 'true'
    #     return response
    if 'user_id' in session:
        return jsonify({"message": "You are already logged in as " + session['username']}), 401
    else:
        if request.method == "POST":
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cur.fetchall()
            if user:
                if bcrypt.check_password_hash(user[0][3], password):
                    session['user_id'] = user[0][0]
                    session['username'] = user[0][1]
                    session['user_type'] = user[0][4]
                    return jsonify({'message': 'Login Successful', 'username': session['username'], 'user_type':session['user_type']}), 200
                else:
                    return jsonify({'message': 'Invalid password'}), 401
            else:
                return jsonify({'message': 'User does not exist'}), 401
        return jsonify({'message': 'Load Login Page'}), 200

@app.route('/api/user_details', methods=['GET'])
def user_details():
    if 'user_id' in session:
        user_id =session["user_id"]
        cur.execute("SELECT ministry_name, department_name, department_description FROM users WHERE user_id=%s", (user_id,))
        user_data = cur.fetchall()[0]
        return jsonify({
            'ministry_name': user_data[0],
            'department_name': user_data[1],
            'department_description': user_data[2]
        })
    else:
        return jsonify({'message': 'No user logged in'}), 400


@app.route('/api/logout', methods=['GET'])
def logout_user():
    if 'user_id' in session:
        session.clear()    
        return jsonify({'message': 'Logout Successful'}), 200
    else:
        return jsonify({'message': 'No user logged in'}), 400

@app.route('/api/policy', methods=['GET', 'POST'])
def policy():
    if 'user_id' in session:        
        if request.method == 'POST':
            if session['user_type']=='Admin':
                data = request.get_json()
                
                department_name = data.get('department_name')
                department_description = data.get('department_description')
                title = data.get('title')
                desc = data.get('description')
                details_type = data.get('details_type')
                details = data.get('details', None)
                authorities_list = data.get('authorities', None)
                reference_list = data.get('references', None)
                pdf_file_path = data.get('pdf_file', None)

                # Update user's department details
                cur.execute("UPDATE users SET department_name = %s, department_description = %s WHERE user_id = %s", (department_name, department_description, session['user_id']))

                # Insert the new policy
                if details_type == 'manual':
                    cur.execute("INSERT INTO policies (title, description, details_type, details, authorities, reference, created_by) VALUES(%s, %s, %s, %s, %s, %s, %s)", (title, desc, details_type, details, str(authorities_list), str(reference_list), session['user_id']))
                else:
                    cur.execute("INSERT INTO policies (title, description, details_type, pdf_file_path, created_by) VALUES(%s, %s, %s, %s, %s)", (title, desc, details_type, pdf_file_path, session['user_id']))
                
                return jsonify({'message': 'Policy created successfully'}), 201
            
            else:
                # Normal user can vote and comment on policies
                data = request.get_json()

                policy_id = data.get('policy_id')
                upvote = data.get('upvote', None)
                downvote = data.get('downvote', None)
                comment = data.get('comment', None)

                # Check if the policy has been voted on by the user
                cur.execute("SELECT vote_type FROM votes WHERE user_id = %s AND policy_id = %s", (session['user_id'], policy_id))
                result = cur.fetchall()

                # Handle voting logic
                if result:
                    vote_type = result[0][0]
                    if vote_type == 'upvote' and upvote:
                        pass  # Prevent double upvote
                    if vote_type == 'downvote' and downvote:
                        pass  # Prevent double downvote
                    elif vote_type == 'downvote' and upvote:
                        cur.execute("UPDATE votes SET vote_type = 'upvote' WHERE user_id = %s AND policy_id = %s", (session['user_id'], policy_id))
                    elif vote_type == 'upvote' and downvote:
                        cur.execute("UPDATE votes SET vote_type = 'downvote' WHERE user_id = %s AND policy_id = %s", (session['user_id'], policy_id))
                else:
                    if upvote:
                        cur.execute("INSERT INTO votes (user_id, policy_id, vote_type) VALUES(%s, %s, 'upvote')", (session['user_id'], policy_id))
                    elif downvote:
                        cur.execute("INSERT INTO votes (user_id, policy_id, vote_type) VALUES(%s, %s, 'downvote')", (session['user_id'], policy_id))

                # Insert comment if provided
                if comment:
                    cur.execute("INSERT INTO comments (user_id, policy_id, comment_text) VALUES(%s, %s, %s)", (session['user_id'], policy_id, comment))

                return redirect('/api/policy')

        else:
            # Updated query to join with users table and fetch ministry_name, department_name, and department_description
            query = """
                SELECT p.policy_id, 
                    p.title, 
                    p.description,
                    p.details,
                    p.authorities,
                    p.reference,
                    p.pdf_file_path,
                    u.ministry_name,  -- Fetch ministry_name from users table
                    u.department_name,  -- Fetch department_name from users table
                    u.department_description,  -- Fetch department_description from users table
                    COALESCE(v.total_upvotes, 0) AS total_upvotes,
                    COALESCE(v.total_downvotes, 0) AS total_downvotes,
                    GROUP_CONCAT(c.comment_text SEPARATOR ' | ') AS comments
                FROM policies p
                LEFT JOIN (
                    SELECT policy_id, 
                        SUM(CASE WHEN vote_type = 'upvote' THEN 1 ELSE 0 END) AS total_upvotes,
                        SUM(CASE WHEN vote_type = 'downvote' THEN 1 ELSE 0 END) AS total_downvotes
                    FROM votes
                    GROUP BY policy_id
                ) v ON p.policy_id = v.policy_id
                LEFT JOIN comments c ON p.policy_id = c.policy_id
                LEFT JOIN users u ON p.created_by = u.user_id  -- Join with users table to fetch ministry and department details
                GROUP BY p.policy_id, p.title, p.description, p.details, p.authorities, p.reference, p.pdf_file_path, u.ministry_name, u.department_name, u.department_description;
            """

            cur.execute(query)
            result = cur.fetchall()
            policies_list = []

            # Process and display results
            for row in result:
                policy_id, title, description, details, authorities, reference, pdf_file_path, ministry_name, department_name, department_description, total_upvotes, total_downvotes, comments = row
                
                # Handle comments being an empty string
                if comments:
                    comments_list = comments.split(' | ')
                else:
                    comments_list = []  # No comments

                policies_list.append({
                    "policy ID": policy_id,
                    "title": title,
                    "description": description,
                    "details": details,
                    "authorities": authorities,
                    "reference": reference,
                    "file": pdf_file_path,
                    "ministry_name": ministry_name,  # Include ministry_name
                    "department_name": department_name,  # Include department_name
                    "department_description": department_description,  # Include department_description
                    "upvotes": total_upvotes,
                    "downvotes": total_downvotes,
                    "comments": comments_list
                })

            return jsonify({"message": "Policies fetched successfully", "policies": policies_list}), 200

    else:
        return jsonify({'message': 'You are not logged in', 'task': 'redirect the user to /api/login'}), 401


@app.route('/api/policy/<int:policy_id>', methods=['GET'])
def get_policy_by_id(policy_id):
    if 'user_id' in session:
        # Query to fetch the details of the specific policy including ministry_name, department_name, and department_description
        query = """
            SELECT p.policy_id, 
                p.title, 
                p.description,
                p.details,
                p.authorities,
                p.reference,
                p.pdf_file_path,
                u.ministry_name,  -- Fetch ministry_name from users table
                u.department_name,  -- Fetch department_name from users table
                u.department_description,  -- Fetch department_description from users table
                p.created_at,
                COALESCE(v.total_upvotes, 0) AS total_upvotes,
                COALESCE(v.total_downvotes, 0) AS total_downvotes,
                GROUP_CONCAT(c.comment_text SEPARATOR ' | ') AS comments
            FROM policies p
            LEFT JOIN (
                SELECT policy_id, 
                    SUM(CASE WHEN vote_type = 'upvote' THEN 1 ELSE 0 END) AS total_upvotes,
                    SUM(CASE WHEN vote_type = 'downvote' THEN 1 ELSE 0 END) AS total_downvotes
                FROM votes
                WHERE policy_id = %s
                GROUP BY policy_id
            ) v ON p.policy_id = v.policy_id
            LEFT JOIN comments c ON p.policy_id = c.policy_id
            LEFT JOIN users u ON p.created_by = u.user_id  -- Join with users table to fetch ministry and department details
            WHERE p.policy_id = %s
            GROUP BY p.policy_id, p.title, p.description, p.details, p.authorities, p.reference, p.pdf_file_path, u.ministry_name, u.department_name, u.department_description, p.created_at;
        """

        cur.execute(query, (policy_id, policy_id))
        result = cur.fetchone()

        if result:
            # Fetch all columns, including ministry and department details
            policy_id, title, description, details, authorities, reference, pdf_file_path, ministry_name, department_name, department_description, created_at, total_upvotes, total_downvotes, comments = result
            
            # Handle comments being an empty string
            if comments:
                comments_list = comments.split(' | ')
            else:
                comments_list = []  # No comments

            policy_data = {
                "policy ID": policy_id,
                "title": title,
                "description": description,
                "details": details,
                "authorities": authorities,
                "reference": reference,
                "file": pdf_file_path,
                "ministry_name": ministry_name,  # Include ministry_name
                "department_name": department_name,  # Include department_name
                "department_description": department_description,  # Include department_description
                "created_at": created_at,
                "upvotes": total_upvotes,
                "downvotes": total_downvotes,
                "comments": comments_list
            }

            return jsonify({"message": "Policy details fetched successfully", "policy": policy_data}), 200
        else:
            return jsonify({"message": "Policy not found"}), 404

    else:
        return jsonify({'message': 'You are not logged in', 'task': 'redirect the user to /api/login'}), 401


@app.route('/api/recent_policies', methods=['GET'])
def recent_policies():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Query to get recent interactions, including ministry_name, department_name, and department_description
        query = """
            SELECT p.policy_id, 
                p.title, 
                p.description, 
                p.details_type, 
                p.details,
                p.authorities, 
                p.reference,
                p.pdf_file_path,
                u.ministry_name,  -- Fetch ministry_name
                u.department_name,  -- Fetch department_name
                u.department_description,  -- Fetch department_description
                p.created_at,
                SUM(CASE WHEN v.vote_type = 'upvote' THEN 1 ELSE 0 END) AS total_upvotes,
                SUM(CASE WHEN v.vote_type = 'downvote' THEN 1 ELSE 0 END) AS total_downvotes,
                GROUP_CONCAT(c.comment_text SEPARATOR ' | ') AS comments,
                GREATEST(COALESCE(MAX(v.voted_at), '1970-01-01'), COALESCE(MAX(c.commented_at), '1970-01-01'), p.created_at) AS last_interaction
            FROM policies p
            LEFT JOIN votes v ON p.policy_id = v.policy_id  -- No user_id filter here for global votes
            LEFT JOIN comments c ON p.policy_id = c.policy_id AND c.user_id = %s -- Filter comments by user
            LEFT JOIN users u ON p.created_by = u.user_id  -- Join with users table to fetch ministry_name, department_name, and department_description
            WHERE v.user_id = %s OR c.user_id = %s OR p.created_at >= NOW() - INTERVAL 30 DAY
            GROUP BY p.policy_id, p.title, p.description, p.details_type, p.details, p.authorities, p.reference, p.pdf_file_path, u.ministry_name, u.department_name, u.department_description, p.created_at
            ORDER BY last_interaction DESC;
        """

        cur.execute(query, (user_id, user_id, user_id))
        result = cur.fetchall()
        policies_list = []

        # Process and display results
        for row in result:
            policy_id, title, description, details_type, details, authorities, reference, pdf_file_path, ministry_name, department_name, department_description, created_at, total_upvotes, total_downvotes, comments, last_interaction = row
            
            # Handle comments being an empty string
            if comments:
                comments_list = comments.split(' | ')
            else:
                comments_list = []  # No comments

            policies_list.append({
                "policy ID": policy_id,
                "title": title,
                "description": description,
                "details_type": details_type,
                "details": details,
                "authorities": authorities,
                "reference": eval(reference),
                "file": pdf_file_path,
                "ministry_name": ministry_name,
                "department_name": department_name,  # Add department_name to response
                "department_description": department_description,  # Add department_description to response
                "created_at": created_at,
                "upvotes": total_upvotes,
                "downvotes": total_downvotes,
                "comments": comments_list
            })

        return jsonify({"message": "Recent policy interactions fetched successfully", "policies": policies_list}), 200

    else:
        return jsonify({'message': 'You are not logged in', 'task': 'redirect the user to /api/login'}), 401

###########Ranked Algo code 
# sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
# sentiment_analyzer = ""

def analyze_sentiment(comment):
    result = sentiment_analyzer(comment)[0]
    if result['label'] == 'POSITIVE':
        return float(result['score'])
    else:
        return -float(result['score'])

def calculate_ranking_score(upvotes, downvotes, comments, created_at):
    vote_score = float(upvotes) - float(downvotes)
    sentiment_scores = [analyze_sentiment(comment) for comment in comments]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
    time_diff = datetime.now() - created_at
    time_decay = 1.0 / (1.0 + float(time_diff.days))
    final_score = (vote_score + avg_sentiment * 10.0) * time_decay
    return final_score
@app.route('/api/ranked_policies', methods=['GET'])
def ranked_policies():
    if 'user_id' in session:
        query = """
            SELECT p.policy_id, 
                p.title, 
                p.description,
                p.details,
                p.authorities,
                p.reference,
                p.pdf_file_path,
                p.created_at,
                COALESCE(v.total_upvotes, 0) AS total_upvotes,
                COALESCE(v.total_downvotes, 0) AS total_downvotes,
                GROUP_CONCAT(c.comment_text SEPARATOR ' | ') AS comments,
                u.ministry_name,
                u.department_name,
                u.department_description
            FROM policies p
            LEFT JOIN (
                SELECT policy_id, 
                    SUM(CASE WHEN vote_type = 'upvote' THEN 1 ELSE 0 END) AS total_upvotes,
                    SUM(CASE WHEN vote_type = 'downvote' THEN 1 ELSE 0 END) AS total_downvotes
                FROM votes
                GROUP BY policy_id
            ) v ON p.policy_id = v.policy_id
            LEFT JOIN comments c ON p.policy_id = c.policy_id
            LEFT JOIN users u ON p.created_by = u.user_id  -- Assuming the user who created the policy is stored in the 'created_by' column
            GROUP BY p.policy_id, p.title, p.description, p.details, p.authorities, p.reference, p.pdf_file_path, p.created_at, u.ministry_name, u.department_name, u.department_description;
        """

        cur.execute(query)
        result = cur.fetchall()
        ranked_policies = []

        for row in result:
            policy_id, title, description, details, authorities, reference, pdf_file_path, created_at, total_upvotes, total_downvotes, comments, ministry_name, department_name, department_description = row
            comments_list = comments.split(' | ') if comments else []

            ranking_score = calculate_ranking_score(total_upvotes, total_downvotes, comments_list, created_at)

            ranked_policies.append({
                "policy_id": policy_id,
                "title": title,
                "description": description,
                "details": details,
                "authorities": authorities,
                "reference": reference,
                "file": pdf_file_path,
                "created_at": created_at,
                "upvotes": total_upvotes,
                "downvotes": total_downvotes,
                "comments": comments_list,
                "ranking_score": ranking_score,
                "ministry_name": ministry_name,
                "department_name": department_name,
                "department_description": department_description
            })

        ranked_policies.sort(key=lambda x: x['ranking_score'], reverse=True)

        return jsonify({"message": "Ranked policies fetched successfully", "ranked_policies": ranked_policies}), 200
    else:
        return jsonify({'message': 'You are not logged in', 'task': 'redirect the user to /api/login'}), 401

@app.route('/api/saved_policies', methods=['GET', 'POST'])
def manage_saved_policies():
    if 'user_id' in session:
        user_id = session['user_id']

        if request.method == 'POST':
            # Save a new policy to the user's saved policies
            data = request.get_json()
            policy_id = data.get('policy_id')

            if policy_id:
                # Check if the policy is already saved by the user
                cur.execute("SELECT * FROM saved_policies WHERE user_id = %s AND policy_id = %s", (user_id, policy_id))
                result = cur.fetchone()

                if result:
                    return jsonify({"message": "Policy already saved"}), 400
                else:
                    cur.execute("INSERT INTO saved_policies (user_id, policy_id) VALUES(%s, %s)", (user_id, policy_id))
                    return jsonify({"message": "Policy saved successfully"}), 201
            else:
                return jsonify({"message": "Policy ID is required"}), 400

        elif request.method == 'GET':
            # Fetch all saved policies for the user
            query = """
                SELECT p.policy_id, 
                       p.title, 
                       p.description, 
                       p.details_type, 
                       p.details,
                       p.authorities, 
                       p.reference,
                       p.pdf_file_path,
                       p.created_by,
                       p.created_at,
                       (SELECT COUNT(*) FROM votes WHERE policy_id = p.policy_id AND vote_type = 'upvote') AS total_upvotes,
                       (SELECT COUNT(*) FROM votes WHERE policy_id = p.policy_id AND vote_type = 'downvote') AS total_downvotes,
                       GROUP_CONCAT(DISTINCT c.comment_text SEPARATOR ' | ') AS comments,
                       MAX(COALESCE(v.voted_at, c.commented_at, p.created_at)) AS last_interaction,
                       u.ministry_name,
                       u.department_name,
                       u.department_description
                FROM saved_policies sp
                JOIN policies p ON sp.policy_id = p.policy_id
                LEFT JOIN votes v ON p.policy_id = v.policy_id
                LEFT JOIN comments c ON p.policy_id = c.policy_id
                LEFT JOIN users u ON p.created_by = u.user_id  -- Join with users to fetch ministry, department info
                WHERE sp.user_id = %s
                GROUP BY p.policy_id, p.title, p.description, p.details_type, p.details, p.authorities, p.reference, 
                         p.pdf_file_path, p.created_by, p.created_at, u.ministry_name, u.department_name, u.department_description
                ORDER BY last_interaction DESC;
            """

            cur.execute(query, (user_id,))
            result = cur.fetchall()

            policies_list = []
            for row in result:
                (policy_id, title, description, details_type, details, authorities, reference, pdf_file_path, 
                 created_by, created_at, total_upvotes, total_downvotes, comments, last_interaction, 
                 ministry_name, department_name, department_description) = row

                # Handle comments being an empty string
                if comments:
                    comments_list = comments.split(' | ')
                else:
                    comments_list = []  # No comments

                policies_list.append({
                    "policy ID": policy_id,
                    "title": title,
                    "description": description,
                    "details_type": details_type,
                    "details": details,
                    "authorities": authorities,
                    "reference": reference,
                    "file": pdf_file_path,
                    "created_by": created_by,
                    "created_at": created_at,
                    "upvotes": total_upvotes,
                    "downvotes": total_downvotes,
                    "comments": comments_list,
                    "last_interaction": last_interaction,
                    "ministry_name": ministry_name,  # Ministry name added
                    "department_name": department_name,  # Department name added
                    "department_description": department_description  # Department description added
                })

            return jsonify({"message": "Saved policies fetched successfully", "policies": policies_list}), 200
    else:
        return jsonify({'message': 'You are not logged in', 'task': 'redirect the user to /api/login'}), 401


@app.route('/api/user_policies', methods=['GET'])
def get_user_policies():
    if 'user_id' in session:
        user_id = session['user_id']

        # Query to get all policies with global upvotes, downvotes, comments, and ministry/department info,
        # while checking the specific user's saved status and last interaction.
        query = """
            SELECT p.policy_id, 
                   p.title, 
                   p.description, 
                   p.details_type, 
                   p.details,
                   p.authorities, 
                   p.reference,
                   p.pdf_file_path,
                   p.created_by,
                   p.created_at,
                   COALESCE(v.total_upvotes, 0) AS total_upvotes,
                   COALESCE(v.total_downvotes, 0) AS total_downvotes,
                   GROUP_CONCAT(DISTINCT gc.comment_text SEPARATOR ' | ') AS comments,  -- Global comments
                   CASE
                       WHEN sp.user_id IS NOT NULL THEN TRUE
                       ELSE FALSE
                   END AS is_saved,
                   GREATEST(COALESCE(MAX(uv.voted_at), '1970-01-01'), COALESCE(MAX(uc.commented_at), '1970-01-01'), p.created_at) AS last_interaction,
                   u.ministry_name, 
                   u.department_name, 
                   u.department_description
            FROM policies p
            LEFT JOIN (
                SELECT policy_id, 
                       SUM(CASE WHEN vote_type = 'upvote' THEN 1 ELSE 0 END) AS total_upvotes,
                       SUM(CASE WHEN vote_type = 'downvote' THEN 1 ELSE 0 END) AS total_downvotes
                FROM votes
                GROUP BY policy_id
            ) v ON p.policy_id = v.policy_id
            LEFT JOIN comments gc ON p.policy_id = gc.policy_id  -- Global comments join (gc for global comments)
            LEFT JOIN saved_policies sp ON p.policy_id = sp.policy_id AND sp.user_id = %s  -- User-specific saved policy
            LEFT JOIN votes uv ON p.policy_id = uv.policy_id AND uv.user_id = %s  -- User-specific votes
            LEFT JOIN comments uc ON p.policy_id = uc.policy_id AND uc.user_id = %s  -- User-specific comments for last interaction
            LEFT JOIN users u ON p.created_by = u.user_id  -- Join with users to fetch ministry, department info
            WHERE (uv.user_id = %s OR uc.user_id = %s OR sp.user_id = %s)  -- User-specific interactions to fetch the policies
            GROUP BY p.policy_id, p.title, p.description, p.details_type, p.details, p.authorities, p.reference, 
                     p.pdf_file_path, p.created_by, p.created_at, u.ministry_name, u.department_name, u.department_description
            ORDER BY last_interaction DESC;
        """

        cur.execute(query, (user_id, user_id, user_id, user_id, user_id, user_id))
        result = cur.fetchall()

        policies_list = []
        for row in result:
            (policy_id, title, description, details_type, details, authorities, reference, pdf_file_path, 
             created_by, created_at, total_upvotes, total_downvotes, comments, is_saved, last_interaction, 
             ministry_name, department_name, department_description) = row

            # Handle comments being an empty string
            if comments:
                comments_list = comments.split(' | ')
            else:
                comments_list = []  # No comments

            policies_list.append({
                "policy ID": policy_id,
                "title": title,
                "description": description,
                "details_type": details_type,
                "details": details,
                "authorities": authorities,
                "reference": reference,
                "file": pdf_file_path,
                "created_by": created_by,
                "created_at": created_at,
                "upvotes": total_upvotes,
                "downvotes": total_downvotes,
                "comments": comments_list,  # Now contains global comments
                "is_saved": bool(is_saved),
                "last_interaction": last_interaction,
                "ministry_name": ministry_name,  # Ministry name added
                "department_name": department_name,  # Department name added
                "department_description": department_description  # Department description added
            })

        return jsonify({"message": "User's interacted policies fetched successfully", "policies": policies_list}), 200
    else:
        return jsonify({'message': 'You are not logged in', 'task': 'redirect the user to /api/login'}), 401

@app.route('/api/summarize_policy', methods=['POST'])
def summarize_policy():
    if 'user_id' in session:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        details = data.get('details')
        ministry_name = data.get('ministry_name')
        department_name = data.get('department_name')
        department_description = data.get('department_description')
        summary_length = data.get('summary_length', 150)

        if not all([title, description, details, ministry_name, department_name, department_description]):
            return jsonify({"message": "Policy information is incomplete"}), 400

        prompt = f"""Summarize this policy concisely in {summary_length} characters or less:

Title: {title}
Ministry: {ministry_name}
Department: {department_name}
Department Description: {department_description}
Description: {description}
Details: {details}"""

        model = GenerativeModel('gemini-1.5-pro')

        response = model.generate_content(prompt)
        summary = response.text[:summary_length]

        return jsonify({
            "message": "Policy summary generated successfully",
            "title": title,
            "summary": summary
        }), 200
    else:
        return jsonify({'message': 'Authentication required', 'action': 'Please log in'}), 401

if __name__ == '__main__':
    app.run(debug=True)

