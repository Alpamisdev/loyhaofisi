from flask import jsonify, request

def register_social_networks_routes(app, get_db, token_required):
    
    @app.route('/api/social-networks', methods=['GET'])
    def get_social_networks():
        """
        Get all social network links
        ---
        tags:
          - Social Networks
        responses:
          200:
            description: List of social network links
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM social_networks")
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/social-networks/<int:network_id>', methods=['GET'])
    def get_social_network(network_id):
        """
        Get a specific social network link
        ---
        tags:
          - Social Networks
        parameters:
          - name: network_id
            in: path
            type: integer
            required: true
            description: ID of the social network
        responses:
          200:
            description: Social network details
          404:
            description: Social network not found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM social_networks WHERE id = ?", (network_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'Social network not found'}), 404
            
        return jsonify(dict(item))
    
    @app.route('/api/social-networks', methods=['POST'])
    @token_required
    def create_social_network(current_user):
        """
        Create a new social network link
        ---
        tags:
          - Social Networks
        security:
          - Bearer: []
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                icon:
                  type: string
                link:
                  type: string
        responses:
          201:
            description: Social network created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('link'):
            return jsonify({'message': 'Name and link are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO social_networks (name, icon, link) VALUES (?, ?, ?)",
            (data['name'], data.get('icon'), data['link'])
        )
        db.commit()
        
        return jsonify({'message': 'Social network created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/social-networks/<int:network_id>', methods=['PUT'])
    @token_required
    def update_social_network(current_user, network_id):
        """
        Update a social network link
        ---
        tags:
          - Social Networks
        security:
          - Bearer: []
        parameters:
          - name: network_id
            in: path
            type: integer
            required: true
            description: ID of the social network
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                icon:
                  type: string
                link:
                  type: string
        responses:
          200:
            description: Social network updated
          400:
            description: Invalid input
          404:
            description: Social network not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if social network exists
        cur.execute("SELECT id FROM social_networks WHERE id = ?", (network_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Social network not found'}), 404
            
        # Update social network
        cur.execute(
            "UPDATE social_networks SET name = ?, icon = ?, link = ? WHERE id = ?",
            (data.get('name'), data.get('icon'), data.get('link'), network_id)
        )
        db.commit()
        
        return jsonify({'message': 'Social network updated'})
    
    @app.route('/api/social-networks/<int:network_id>', methods=['DELETE'])
    @token_required
    def delete_social_network(current_user, network_id):
        """
        Delete a social network link
        ---
        tags:
          - Social Networks
        security:
          - Bearer: []
        parameters:
          - name: network_id
            in: path
            type: integer
            required: true
            description: ID of the social network
        responses:
          200:
            description: Social network deleted
          404:
            description: Social network not found
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if social network exists
        cur.execute("SELECT id FROM social_networks WHERE id = ?", (network_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Social network not found'}), 404
            
        # Delete social network
        cur.execute("DELETE FROM social_networks WHERE id = ?", (network_id,))
        db.commit()
        
        return jsonify({'message': 'Social network deleted'})
