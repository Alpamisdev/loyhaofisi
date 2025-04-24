from flask import jsonify, request

def register_documents_routes(app, get_db, token_required):
    
    # Document Categories
    @app.route('/api/documents/categories', methods=['GET'])
    def get_document_categories():
        """
        Get all document categories
        ---
        tags:
          - Documents
        responses:
          200:
            description: List of document categories
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM documents_categories")
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/documents/categories/<int:category_id>', methods=['GET'])
    def get_document_category(category_id):
        """
        Get a specific document category
        ---
        tags:
          - Documents
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the document category
        responses:
          200:
            description: Document category details
          404:
            description: Document category not found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM documents_categories WHERE id = ?", (category_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'Document category not found'}), 404
            
        return jsonify(dict(item))
    
    @app.route('/api/documents/categories', methods=['POST'])
    @token_required
    def create_document_category(current_user):
        """
        Create a new document category
        ---
        tags:
          - Documents
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
            description: Document category created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO documents_categories (name) VALUES (?)",
            (data['name'],)
        )
        db.commit()
        
        return jsonify({'message': 'Document category created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/documents/categories/<int:category_id>', methods=['PUT'])
    @token_required
    def update_document_category(current_user, category_id):
        """
        Update a document category
        ---
        tags:
          - Documents
        security:
          - Bearer: []
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the document category
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
            description: Document category updated
          400:
            description: Invalid input
          404:
            description: Document category not found
        """
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists
        cur.execute("SELECT id FROM documents_categories WHERE id = ?", (category_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Document category not found'}), 404
            
        # Update category
        cur.execute(
            "UPDATE documents_categories SET name = ? WHERE id = ?",
            (data['name'], category_id)
        )
        db.commit()
        
        return jsonify({'message': 'Document category updated'})
    
    @app.route('/api/documents/categories/<int:category_id>', methods=['DELETE'])
    @token_required
    def delete_document_category(current_user, category_id):
        """
        Delete a document category
        ---
        tags:
          - Documents
        security:
          - Bearer: []
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the document category
        responses:
          200:
            description: Document category deleted
          404:
            description: Document category not found
          400:
            description: Cannot delete category with documents
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists
        cur.execute("SELECT id FROM documents_categories WHERE id = ?", (category_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Document category not found'}), 404
            
        # Check if category has documents
        cur.execute("SELECT COUNT(*) as count FROM documents_items WHERE category_id = ?", (category_id,))
        count = cur.fetchone()['count']
        if count > 0:
            return jsonify({'message': 'Cannot delete category with documents'}), 400
            
        # Delete category
        cur.execute("DELETE FROM documents_categories WHERE id = ?", (category_id,))
        db.commit()
        
        return jsonify({'message': 'Document category deleted'})
    
    # Document Items
    @app.route('/api/documents/items', methods=['GET'])
    def get_document_items():
        """
        Get all document items
        ---
        tags:
          - Documents
        parameters:
          - name: category_id
            in: query
            type: integer
            required: false
            description: Filter by category ID
        responses:
          200:
            description: List of document items
        """
        category_id = request.args.get('category_id')
        
        db = get_db()
        cur = db.cursor()
        
        if category_id:
            cur.execute("""
                SELECT di.*, dc.name as category_name 
                FROM documents_items di
                LEFT JOIN documents_categories dc ON di.category_id = dc.id
                WHERE di.category_id = ?
            """, (category_id,))
        else:
            cur.execute("""
                SELECT di.*, dc.name as category_name 
                FROM documents_items di
                LEFT JOIN documents_categories dc ON di.category_id = dc.id
            """)
            
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/documents/items/<int:item_id>', methods=['GET'])
    def get_document_item(item_id):
        """
        Get a specific document item
        ---
        tags:
          - Documents
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the document item
        responses:
          200:
            description: Document item details
          404:
            description: Document item not found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT di.*, dc.name as category_name 
            FROM documents_items di
            LEFT JOIN documents_categories dc ON di.category_id = dc.id
            WHERE di.id = ?
        """, (item_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'Document item not found'}), 404
            
        return jsonify(dict(item))
    
    @app.route('/api/documents/items', methods=['POST'])
    @token_required
    def create_document_item(current_user):
        """
        Create a new document item
        ---
        tags:
          - Documents
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
                name:
                  type: string
                link:
                  type: string
        responses:
          201:
            description: Document item created
          400:
            description: Invalid input
          404:
            description: Category not found
        """
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('name') or not data.get('link'):
            return jsonify({'message': 'Title, name, and link are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists if provided
        if data.get('category_id'):
            cur.execute("SELECT id FROM documents_categories WHERE id = ?", (data['category_id'],))
            if not cur.fetchone():
                return jsonify({'message': 'Document category not found'}), 404
        
        cur.execute(
            "INSERT INTO documents_items (category_id, title, name, link) VALUES (?, ?, ?, ?)",
            (data.get('category_id'), data['title'], data['name'], data['link'])
        )
        db.commit()
        
        return jsonify({'message': 'Document item created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/documents/items/<int:item_id>', methods=['PUT'])
    @token_required
    def update_document_item(current_user, item_id):
        """
        Update a document item
        ---
        tags:
          - Documents
        security:
          - Bearer: []
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the document item
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
                name:
                  type: string
                link:
                  type: string
        responses:
          200:
            description: Document item updated
          400:
            description: Invalid input
          404:
            description: Document item not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if document item exists
        cur.execute("SELECT id FROM documents_items WHERE id = ?", (item_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Document item not found'}), 404
            
        # Check if category exists if provided
        if data.get('category_id'):
            cur.execute("SELECT id FROM documents_categories WHERE id = ?", (data['category_id'],))
            if not cur.fetchone():
                return jsonify({'message': 'Document category not found'}), 404
            
        # Update document item
        cur.execute(
            """UPDATE documents_items 
               SET category_id = ?, title = ?, name = ?, link = ? 
               WHERE id = ?""",
            (data.get('category_id'), data.get('title'), data.get('name'), 
             data.get('link'), item_id)
        )
        db.commit()
        
        return jsonify({'message': 'Document item updated'})
    
    @app.route('/api/documents/items/<int:item_id>', methods=['DELETE'])
    @token_required
    def delete_document_item(current_user, item_id):
        """
        Delete a document item
        ---
        tags:
          - Documents
        security:
          - Bearer: []
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the document item
        responses:
          200:
            description: Document item deleted
          404:
            description: Document item not found
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if document item exists
        cur.execute("SELECT id FROM documents_items WHERE id = ?", (item_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Document item not found'}), 404
            
        # Delete document item
        cur.execute("DELETE FROM documents_items WHERE id = ?", (item_id,))
        db.commit()
        
        return jsonify({'message': 'Document item deleted'})
