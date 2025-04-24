from flask import jsonify, request

def register_year_name_routes(app, get_db, token_required):
    
    @app.route('/api/year-name', methods=['GET'])
    def get_year_names():
        """
        Get all year name banners
        ---
        tags:
          - Year Name
        responses:
          200:
            description: List of year name banners
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM year_name ORDER BY id DESC")
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/year-name/current', methods=['GET'])
    def get_current_year_name():
        """
        Get the most recent year name banner
        ---
        tags:
          - Year Name
        responses:
          200:
            description: Current year name banner
          404:
            description: No year name banners found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM year_name ORDER BY id DESC LIMIT 1")
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'No year name found'}), 404
            
        return jsonify(dict(item))
    
    @app.route('/api/year-name', methods=['POST'])
    @token_required
    def create_year_name(current_user):
        """
        Create a new year name banner
        ---
        tags:
          - Year Name
        security:
          - Bearer: []
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                text:
                  type: string
                img:
                  type: string
        responses:
          201:
            description: Year name banner created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('text'):
            return jsonify({'message': 'Year name text is required'}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO year_name (text, img) VALUES (?, ?)",
            (data['text'], data.get('img'))
        )
        db.commit()
        
        return jsonify({'message': 'Year name created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/year-name/<int:year_id>', methods=['PUT'])
    @token_required
    def update_year_name(current_user, year_id):
        """
        Update a year name banner
        ---
        tags:
          - Year Name
        security:
          - Bearer: []
        parameters:
          - name: year_id
            in: path
            type: integer
            required: true
            description: ID of the year name banner
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                text:
                  type: string
                img:
                  type: string
        responses:
          200:
            description: Year name banner updated
          400:
            description: Invalid input
          404:
            description: Year name banner not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if year name exists
        cur.execute("SELECT id FROM year_name WHERE id = ?", (year_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Year name not found'}), 404
            
        # Update year name
        cur.execute(
            "UPDATE year_name SET text = ?, img = ? WHERE id = ?",
            (data.get('text'), data.get('img'), year_id)
        )
        db.commit()
        
        return jsonify({'message': 'Year name updated'})
    
    @app.route('/api/year-name/<int:year_id>', methods=['DELETE'])
    @token_required
    def delete_year_name(current_user, year_id):
        """
        Delete a year name banner
        ---
        tags:
          - Year Name
        security:
          - Bearer: []
        parameters:
          - name: year_id
            in: path
            type: integer
            required: true
            description: ID of the year name banner
        responses:
          200:
            description: Year name banner deleted
          404:
            description: Year name banner not found
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if year name exists
        cur.execute("SELECT id FROM year_name WHERE id = ?", (year_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Year name not found'}), 404
            
        # Delete year name
        cur.execute("DELETE FROM year_name WHERE id = ?", (year_id,))
        db.commit()
        
        return jsonify({'message': 'Year name deleted'})
