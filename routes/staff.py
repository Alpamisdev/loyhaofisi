from flask import jsonify, request

def register_staff_routes(app, get_db, token_required):
    
    @app.route('/api/staff', methods=['GET'])
    def get_staff_members():
        """
        Get all staff members
        ---
        tags:
          - Staff
        responses:
          200:
            description: List of staff members
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM staff")
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/staff/<int:staff_id>', methods=['GET'])
    def get_staff_member(staff_id):
        """
        Get a specific staff member
        ---
        tags:
          - Staff
        parameters:
          - name: staff_id
            in: path
            type: integer
            required: true
            description: ID of the staff member
        responses:
          200:
            description: Staff member details
          404:
            description: Staff member not found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM staff WHERE id = ?", (staff_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'Staff member not found'}), 404
            
        return jsonify(dict(item))
    
    @app.route('/api/staff', methods=['POST'])
    @token_required
    def create_staff_member(current_user):
        """
        Create a new staff member
        ---
        tags:
          - Staff
        security:
          - Bearer: []
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                position:
                  type: string
                full_name:
                  type: string
                email:
                  type: string
                phone:
                  type: string
                photo:
                  type: string
        responses:
          201:
            description: Staff member created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('position') or not data.get('full_name'):
            return jsonify({'message': 'Position and full name are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO staff (position, full_name, email, phone, photo) VALUES (?, ?, ?, ?, ?)",
            (data['position'], data['full_name'], data.get('email'), data.get('phone'), data.get('photo'))
        )
        db.commit()
        
        return jsonify({'message': 'Staff member created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/staff/<int:staff_id>', methods=['PUT'])
    @token_required
    def update_staff_member(current_user, staff_id):
        """
        Update a staff member
        ---
        tags:
          - Staff
        security:
          - Bearer: []
        parameters:
          - name: staff_id
            in: path
            type: integer
            required: true
            description: ID of the staff member
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                position:
                  type: string
                full_name:
                  type: string
                email:
                  type: string
                phone:
                  type: string
                photo:
                  type: string
        responses:
          200:
            description: Staff member updated
          400:
            description: Invalid input
          404:
            description: Staff member not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if staff member exists
        cur.execute("SELECT id FROM staff WHERE id = ?", (staff_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Staff member not found'}), 404
            
        # Update staff member
        cur.execute(
            """UPDATE staff 
               SET position = ?, full_name = ?, email = ?, phone = ?, photo = ? 
               WHERE id = ?""",
            (data.get('position'), data.get('full_name'), data.get('email'),
             data.get('phone'), data.get('photo'), staff_id)
        )
        db.commit()
        
        return jsonify({'message': 'Staff member updated'})
    
    @app.route('/api/staff/<int:staff_id>', methods=['DELETE'])
    @token_required
    def delete_staff_member(current_user, staff_id):
        """
        Delete a staff member
        ---
        tags:
          - Staff
        security:
          - Bearer: []
        parameters:
          - name: staff_id
            in: path
            type: integer
            required: true
            description: ID of the staff member
        responses:
          200:
            description: Staff member deleted
          404:
            description: Staff member not found
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if staff member exists
        cur.execute("SELECT id FROM staff WHERE id = ?", (staff_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Staff member not found'}), 404
            
        # Delete staff member
        cur.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
        db.commit()
        
        return jsonify({'message': 'Staff member deleted'})
