from flask import jsonify, request

def register_menu_routes(app, get_db, token_required):
    
    @app.route('/api/menu', methods=['GET'])
    def get_menu_items():
        """
        Get all menu items
        ---
        tags:
          - Menu
        parameters:
          - name: include_deleted
            in: query
            type: boolean
            required: false
            default: false
            description: Whether to include soft-deleted records
        responses:
          200:
            description: List of menu items
        """
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        db = get_db()
        cur = db.cursor()
        
        if include_deleted:
            cur.execute("SELECT * FROM menu ORDER BY id")
        else:
            cur.execute("SELECT * FROM menu WHERE is_deleted = 0 ORDER BY id")
        
        menu_items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(menu_items)
    
    @app.route('/api/menu/<int:menu_id>', methods=['GET'])
    def get_menu_item(menu_id):
        """
        Get a specific menu item
        ---
        tags:
          - Menu
        parameters:
          - name: menu_id
            in: path
            type: integer
            required: true
            description: ID of the menu item
          - name: include_deleted
            in: query
            type: boolean
            required: false
            default: false
            description: Whether to include soft-deleted records
        responses:
          200:
            description: Menu item details
          404:
            description: Menu item not found
        """
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        db = get_db()
        cur = db.cursor()
        
        if include_deleted:
            cur.execute("SELECT * FROM menu WHERE id = ?", (menu_id,))
        else:
            cur.execute("SELECT * FROM menu WHERE id = ? AND is_deleted = 0", (menu_id,))
        
        menu_item = cur.fetchone()
        
        if not menu_item:
            return jsonify({'message': 'Menu item not found'}), 404
        
        return jsonify(dict(menu_item))
    
    @app.route('/api/menu', methods=['POST'])
    @token_required
    def create_menu_item(current_user):
        """
        Create a new menu item
        ---
        tags:
          - Menu
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
        responses:
          201:
            description: Menu item created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Menu name is required'}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO menu (name, icon) VALUES (?, ?)",
            (data['name'], data.get('icon'))
        )
        db.commit()
        
        return jsonify({'message': 'Menu item created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/menu/<int:menu_id>', methods=['PUT'])
    @token_required
    def update_menu_item(current_user, menu_id):
        """
        Update a menu item
        ---
        tags:
          - Menu
        security:
          - Bearer: []
        parameters:
          - name: menu_id
            in: path
            type: integer
            required: true
            description: ID of the menu item
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
        responses:
          200:
            description: Menu item updated
          400:
            description: Invalid input
          404:
            description: Menu item not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if menu item exists
        cur.execute("SELECT id FROM menu WHERE id = ?", (menu_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Menu item not found'}), 404
            
        # Update menu item
        cur.execute(
            "UPDATE menu SET name = ?, icon = ? WHERE id = ?",
            (data.get('name'), data.get('icon'), menu_id)
        )
        db.commit()
        
        return jsonify({'message': 'Menu item updated'})
    
    @app.route('/api/menu/<int:menu_id>', methods=['DELETE'])
    @token_required
    def delete_menu_item(current_user, menu_id):
        """
        Soft delete a menu item
        ---
        tags:
          - Menu
        security:
          - Bearer: []
        parameters:
          - name: menu_id
            in: path
            type: integer
            required: true
            description: ID of the menu item
        responses:
          200:
            description: Menu item deleted
          404:
            description: Menu item not found
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if menu item exists
        cur.execute("SELECT id FROM menu WHERE id = ? AND is_deleted = 0", (menu_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Menu item not found'}), 404
        
        # Soft delete menu item
        cur.execute("UPDATE menu SET is_deleted = 1 WHERE id = ?", (menu_id,))
        db.commit()
        
        return jsonify({'message': 'Menu item deleted'})

    @app.route('/api/menu/links', methods=['GET'])
    def get_menu_links():
        """
        Get all menu links
        ---
        tags:
          - Menu Links
        responses:
          200:
            description: List of menu links
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT ml.*, m.name as menu_name 
            FROM menu_links ml
            JOIN menu m ON ml.menu_id = m.id
            ORDER BY ml.position
        """)
        menu_links = [dict(row) for row in cur.fetchall()]
        
        return jsonify(menu_links)

    @app.route('/api/menu/links', methods=['POST'])
    @token_required
    def create_menu_link(current_user):
        """
        Create a new menu link
        ---
        tags:
          - Menu Links
        security:
          - Bearer: []
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                menu_id:
                  type: integer
                target_type:
                  type: string
                target_id:
                  type: integer
                label:
                  type: string
                position:
                  type: integer
        responses:
          201:
            description: Menu link created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('menu_id') or not data.get('target_type'):
            return jsonify({'message': 'Menu ID and target type are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Verify menu ID exists
        cur.execute("SELECT id FROM menu WHERE id = ?", (data['menu_id'],))
        if not cur.fetchone():
            return jsonify({'message': 'Menu item not found'}), 404
            
        cur.execute(
            """INSERT INTO menu_links 
               (menu_id, target_type, target_id, label, position) 
               VALUES (?, ?, ?, ?, ?)""",
            (data['menu_id'], data['target_type'], data.get('target_id'), 
             data.get('label'), data.get('position', 0))
        )
        db.commit()
        
        return jsonify({'message': 'Menu link created', 'id': cur.lastrowid}), 201
