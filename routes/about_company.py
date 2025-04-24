from flask import jsonify, request
import datetime

def register_about_company_routes(app, get_db, token_required):
    
    # Main about company info
    @app.route('/api/about-company', methods=['GET'])
    def get_about_company():
        """
        Get about company information
        ---
        tags:
          - About Company
        parameters:
          - name: increment_views
            in: query
            type: boolean
            required: false
            description: Increment view count
        responses:
          200:
            description: About company information
          404:
            description: About company information not found
        """
        increment_views = request.args.get('increment_views', 'false').lower() == 'true'
        
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM about_company ORDER BY id DESC LIMIT 1")
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'About company information not found'}), 404
        
        # Increment views if requested
        if increment_views:
            new_views = item['views'] + 1
            cur.execute("UPDATE about_company SET views = ? WHERE id = ?", (new_views, item['id']))
            db.commit()
            item = dict(item)
            item['views'] = new_views
            
        return jsonify(dict(item))
    
    @app.route('/api/about-company', methods=['POST'])
    @token_required
    def create_about_company(current_user):
        """
        Create about company information
        ---
        tags:
          - About Company
        security:
          - Bearer: []
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                img:
                  type: string
                text:
                  type: string
        responses:
          201:
            description: About company information created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('text'):
            return jsonify({'message': 'Title and text are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        now = datetime.datetime.now().isoformat()
        
        cur.execute(
            "INSERT INTO about_company (title, img, date_time, views, text) VALUES (?, ?, ?, ?, ?)",
            (data['title'], data.get('img'), now, 0, data['text'])
        )
        db.commit()
        
        return jsonify({'message': 'About company information created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/about-company/<int:about_id>', methods=['PUT'])
    @token_required
    def update_about_company(current_user, about_id):
        """
        Update about company information
        ---
        tags:
          - About Company
        security:
          - Bearer: []
        parameters:
          - name: about_id
            in: path
            type: integer
            required: true
            description: ID of the about company record
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                img:
                  type: string
                text:
                  type: string
        responses:
          200:
            description: About company information updated
          400:
            description: Invalid input
          404:
            description: About company information not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if about company exists
        cur.execute("SELECT id FROM about_company WHERE id = ?", (about_id,))
        if not cur.fetchone():
            return jsonify({'message': 'About company information not found'}), 404
            
        # Update about company
        cur.execute(
            "UPDATE about_company SET title = ?, img = ?, text = ? WHERE id = ?",
            (data.get('title'), data.get('img'), data.get('text'), about_id)
        )
        db.commit()
        
        return jsonify({'message': 'About company information updated'})
    
    # About company categories
    @app.route('/api/about-company/categories', methods=['GET'])
    def get_about_company_categories():
        """
        Get all about company categories
        ---
        tags:
          - About Company
        responses:
          200:
            description: List of about company categories
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM about_company_categories")
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/about-company/categories/<int:category_id>', methods=['GET'])
    def get_about_company_category(category_id):
        """
        Get a specific about company category
        ---
        tags:
          - About Company
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the category
        responses:
          200:
            description: About company category details
          404:
            description: About company category not found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM about_company_categories WHERE id = ?", (category_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'About company category not found'}), 404
            
        return jsonify(dict(item))
    
    @app.route('/api/about-company/categories', methods=['POST'])
    @token_required
    def create_about_company_category(current_user):
        """
        Create a new about company category
        ---
        tags:
          - About Company
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
        responses:
          201:
            description: About company category created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO about_company_categories (name) VALUES (?)",
            (data['name'],)
        )
        db.commit()
        
        return jsonify({'message': 'About company category created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/about-company/categories/<int:category_id>', methods=['PUT'])
    @token_required
    def update_about_company_category(current_user, category_id):
        """
        Update an about company category
        ---
        tags:
          - About Company
        security:
          - Bearer: []
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the category
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
        responses:
          200:
            description: About company category updated
          400:
            description: Invalid input
          404:
            description: About company category not found
        """
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists
        cur.execute("SELECT id FROM about_company_categories WHERE id = ?", (category_id,))
        if not cur.fetchone():
            return jsonify({'message': 'About company category not found'}), 404
            
        # Update category
        cur.execute(
            "UPDATE about_company_categories SET name = ? WHERE id = ?",
            (data['name'], category_id)
        )
        db.commit()
        
        return jsonify({'message': 'About company category updated'})
    
    @app.route('/api/about-company/categories/<int:category_id>', methods=['DELETE'])
    @token_required
    def delete_about_company_category(current_user, category_id):
        """
        Delete an about company category
        ---
        tags:
          - About Company
        security:
          - Bearer: []
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the category
        responses:
          200:
            description: About company category deleted
          404:
            description: About company category not found
          400:
            description: Cannot delete category with items
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists
        cur.execute("SELECT id FROM about_company_categories WHERE id = ?", (category_id,))
        if not cur.fetchone():
            return jsonify({'message': 'About company category not found'}), 404
            
        # Check if category has items
        cur.execute("SELECT COUNT(*) as count FROM about_company_category_items WHERE category_id = ?", (category_id,))
        count = cur.fetchone()['count']
        if count > 0:
            return jsonify({'message': 'Cannot delete category with items'}), 400
            
        # Delete category
        cur.execute("DELETE FROM about_company_categories WHERE id = ?", (category_id,))
        db.commit()
        
        return jsonify({'message': 'About company category deleted'})
    
    # About company category items
    @app.route('/api/about-company/items', methods=['GET'])
    def get_about_company_items():
        """
        Get all about company category items
        ---
        tags:
          - About Company
        parameters:
          - name: category_id
            in: query
            type: integer
            required: false
            description: Filter by category ID
        responses:
          200:
            description: List of about company category items
        """
        category_id = request.args.get('category_id')
        
        db = get_db()
        cur = db.cursor()
        
        if category_id:
            cur.execute("""
                SELECT i.*, c.name as category_name 
                FROM about_company_category_items i
                LEFT JOIN about_company_categories c ON i.category_id = c.id
                WHERE i.category_id = ?
                ORDER BY i.date_time DESC
            """, (category_id,))
        else:
            cur.execute("""
                SELECT i.*, c.name as category_name 
                FROM about_company_category_items i
                LEFT JOIN about_company_categories c ON i.category_id = c.id
                ORDER BY i.date_time DESC
            """)
            
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/about-company/items/<int:item_id>', methods=['GET'])
    def get_about_company_item(item_id):
        """
        Get a specific about company category item
        ---
        tags:
          - About Company
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the item
          - name: increment_views
            in: query
            type: boolean
            required: false
            description: Increment view count
        responses:
          200:
            description: About company category item details
          404:
            description: About company category item not found
        """
        increment_views = request.args.get('increment_views', 'false').lower() == 'true'
        
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT i.*, c.name as category_name 
            FROM about_company_category_items i
            LEFT JOIN about_company_categories c ON i.category_id = c.id
            WHERE i.id = ?
        """, (item_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'About company category item not found'}), 404
        
        # Increment views if requested
        if increment_views:
            new_views = item['views'] + 1
            cur.execute("UPDATE about_company_category_items SET views = ? WHERE id = ?", (new_views, item_id))
            db.commit()
            item = dict(item)
            item['views'] = new_views
            
        return jsonify(dict(item))
    
    @app.route('/api/about-company/items', methods=['POST'])
    @token_required
    def create_about_company_item(current_user):
        """
        Create a new about company category item
        ---
        tags:
          - About Company
        security:
          - Bearer: []
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                category_id:
                  type: integer
                title:
                  type: string
                text:
                  type: string
                feedback_id:
                  type: integer
        responses:
          201:
            description: About company category item created
          400:
            description: Invalid input
          404:
            description: Category not found
        """
        data = request.get_json()
        
        if not data or not data.get('category_id') or not data.get('title') or not data.get('text'):
            return jsonify({'message': 'Category ID, title and text are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists
        cur.execute("SELECT id FROM about_company_categories WHERE id = ?", (data['category_id'],))
        if not cur.fetchone():
            return jsonify({'message': 'About company category not found'}), 404
            
        # Check if feedback exists if provided
        if data.get('feedback_id'):
            cur.execute("SELECT id FROM feedback WHERE id = ?", (data['feedback_id'],))
            if not cur.fetchone():
                return jsonify({'message': 'Feedback not found'}), 404
        
        now = datetime.datetime.now().isoformat()
        
        cur.execute(
            """INSERT INTO about_company_category_items 
               (category_id, title, text, views, date_time, feedback_id) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (data['category_id'], data['title'], data['text'], 0, now, data.get('feedback_id'))
        )
        db.commit()
        
        return jsonify({'message': 'About company category item created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/about-company/items/<int:item_id>', methods=['PUT'])
    @token_required
    def update_about_company_item(current_user, item_id):
        """
        Update an about company category item
        ---
        tags:
          - About Company
        security:
          - Bearer: []
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the item
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                category_id:
                  type: integer
                title:
                  type: string
                text:
                  type: string
                feedback_id:
                  type: integer
        responses:
          200:
            description: About company category item updated
          400:
            description: Invalid input
          404:
            description: Item not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if item exists
        cur.execute("SELECT id FROM about_company_category_items WHERE id = ?", (item_id,))
        if not cur.fetchone():
            return jsonify({'message': 'About company category item not found'}), 404
            
        # Check if category exists if provided
        if data.get('category_id'):
            cur.execute("SELECT id FROM about_company_categories WHERE id = ?", (data['category_id'],))
            if not cur.fetchone():
                return jsonify({'message': 'About company category not found'}), 404
                
        # Check if feedback exists if provided
        if data.get('feedback_id'):
            cur.execute("SELECT id FROM feedback WHERE id = ?", (data['feedback_id'],))
            if not cur.fetchone():
                return jsonify({'message': 'Feedback not found'}), 404
        
        # Update item
        cur.execute(
            """UPDATE about_company_category_items 
               SET category_id = ?, title = ?, text = ?, feedback_id = ? 
               WHERE id = ?""",
            (data.get('category_id'), data.get('title'), data.get('text'), 
             data.get('feedback_id'), item_id)
        )
        db.commit()
        
        return jsonify({'message': 'About company category item updated'})
    
    @app.route('/api/about-company/items/<int:item_id>', methods=['DELETE'])
    @token_required
    def delete_about_company_item(current_user, item_id):
        """
        Delete an about company category item
        ---
        tags:
          - About Company
        security:
          - Bearer: []
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the item
        responses:
          200:
            description: About company category item deleted
          404:
            description: Item not found
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if item exists
        cur.execute("SELECT id FROM about_company_category_items WHERE id = ?", (item_id,))
        if not cur.fetchone():
            return jsonify({'message': 'About company category item not found'}), 404
            
        # Delete item
        cur.execute("DELETE FROM about_company_category_items WHERE id = ?", (item_id,))
        db.commit()
        
        return jsonify({'message': 'About company category item deleted'})
