from flask import jsonify, request
import datetime

def register_feedback_routes(app, get_db, token_required):
    
    @app.route('/api/feedback', methods=['GET'])
    @token_required
    def get_feedback_items(current_user):
        """
        Get all feedback messages
        ---
        tags:
          - Feedback
        security:
          - Bearer: []
        parameters:
          - name: include_deleted
            in: query
            type: boolean
            required: false
            default: false
            description: Whether to include soft-deleted records
        responses:
          200:
            description: List of feedback messages
        """
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        db = get_db()
        cur = db.cursor()
        
        if include_deleted:
            cur.execute("SELECT * FROM feedback ORDER BY created_at DESC")
        else:
            cur.execute("SELECT * FROM feedback WHERE is_deleted = 0 ORDER BY created_at DESC")
            
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/feedback/<int:feedback_id>', methods=['GET'])
    @token_required
    def get_feedback_item(current_user, feedback_id):
        """
        Get a specific feedback message
        ---
        tags:
          - Feedback
        security:
          - Bearer: []
        parameters:
          - name: feedback_id
            in: path
            type: integer
            required: true
            description: ID of the feedback message
        responses:
          200:
            description: Feedback message details
          404:
            description: Feedback message not found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'Feedback not found'}), 404
            
        return jsonify(dict(item))
    
    @app.route('/api/feedback', methods=['POST'])
    def create_feedback():
        """
        Submit a new feedback message
        ---
        tags:
          - Feedback
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                full_name:
                  type: string
                phone_number:
                  type: string
                email:
                  type: string
                theme:
                  type: string
                text:
                  type: string
        responses:
          201:
            description: Feedback submitted
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('full_name') or not data.get('text'):
            return jsonify({'message': 'Full name and text are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        now = datetime.datetime.now().isoformat()
        
        cur.execute(
            "INSERT INTO feedback (full_name, phone_number, email, theme, text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (data['full_name'], data.get('phone_number'), data.get('email'), data.get('theme'), data['text'], now)
        )
        db.commit()
        
        return jsonify({'message': 'Feedback submitted', 'id': cur.lastrowid}), 201
    
    @app.route('/api/feedback/<int:feedback_id>', methods=['DELETE'])
    @token_required
    def delete_feedback(current_user, feedback_id):
        """
        Soft delete a feedback message
        ---
        tags:
          - Feedback
        security:
          - Bearer: []
        parameters:
          - name: feedback_id
            in: path
            type: integer
            required: true
            description: ID of the feedback message
        responses:
          200:
            description: Feedback message deleted
          404:
            description: Feedback message not found
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if feedback exists
        cur.execute("SELECT id FROM feedback WHERE id = ? AND is_deleted = 0", (feedback_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Feedback not found'}), 404
            
        # Soft delete feedback
        cur.execute("UPDATE feedback SET is_deleted = 1 WHERE id = ?", (feedback_id,))
        db.commit()
        
        return jsonify({'message': 'Feedback deleted'})
