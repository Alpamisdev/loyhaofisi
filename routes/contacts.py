from flask import jsonify, request

def register_contacts_routes(app, get_db, token_required):
    
    @app.route('/api/contacts', methods=['GET'])
    def get_contacts():
        """
        Get company contact information
        ---
        tags:
          - Contacts
        responses:
          200:
            description: Contact information
          404:
            description: No contact information found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM contacts LIMIT 1")
        contacts = cur.fetchone()
        
        if not contacts:
            return jsonify({'message': 'No contacts found'}), 404
            
        return jsonify(dict(contacts))
    
    @app.route('/api/contacts', methods=['POST'])
    @token_required
    def create_contacts(current_user):
        """
        Create company contact information
        ---
        tags:
          - Contacts
        security:
          - Bearer: []
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                address:
                  type: string
                phone_number:
                  type: string
                email:
                  type: string
        responses:
          201:
            description: Contact information created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if contacts already exist
        cur.execute("SELECT COUNT(*) as count FROM contacts")
        count = cur.fetchone()['count']
        
        if count > 0:
            # Update existing contacts instead of creating new
            cur.execute("UPDATE contacts SET address = ?, phone_number = ?, email = ?", 
                      (data.get('address'), data.get('phone_number'), data.get('email')))
            db.commit()
            return jsonify({'message': 'Contacts updated'}), 200
            
        # Create new contacts
        cur.execute(
            "INSERT INTO contacts (address, phone_number, email) VALUES (?, ?, ?)",
            (data.get('address'), data.get('phone_number'), data.get('email'))
        )
        db.commit()
        
        return jsonify({'message': 'Contacts created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
    @token_required
    def update_contacts(current_user, contact_id):
        """
        Update company contact information
        ---
        tags:
          - Contacts
        security:
          - Bearer: []
        parameters:
          - name: contact_id
            in: path
            type: integer
            required: true
            description: ID of the contact record
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                address:
                  type: string
                phone_number:
                  type: string
                email:
                  type: string
        responses:
          200:
            description: Contact information updated
          400:
            description: Invalid input
          404:
            description: Contact information not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if contacts exist
        cur.execute("SELECT id FROM contacts WHERE id = ?", (contact_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Contacts not found'}), 404
            
        # Update contacts
        cur.execute(
            "UPDATE contacts SET address = ?, phone_number = ?, email = ? WHERE id = ?",
            (data.get('address'), data.get('phone_number'), data.get('email'), contact_id)
        )
        db.commit()
        
        return jsonify({'message': 'Contacts updated'})
