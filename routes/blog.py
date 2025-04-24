from flask import jsonify, request
import datetime

def register_blog_routes(app, get_db, token_required):
    
    # Blog Categories
    @app.route('/api/blog/categories', methods=['GET'])
    def get_blog_categories():
        """
        Get all blog categories
        ---
        tags:
          - Blog
        parameters:
          - name: include_deleted
            in: query
            type: boolean
            required: false
            default: false
            description: Whether to include soft-deleted records
        responses:
          200:
            description: List of blog categories
        """
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        db = get_db()
        cur = db.cursor()
        
        if include_deleted:
            cur.execute("SELECT * FROM blog_categories")
        else:
            cur.execute("SELECT * FROM blog_categories WHERE is_deleted = 0")
        
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/blog/categories/<int:category_id>', methods=['GET'])
    def get_blog_category(category_id):
        """
        Get a specific blog category
        ---
        tags:
          - Blog
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the blog category
        responses:
          200:
            description: Blog category details
          404:
            description: Blog category not found
        """
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM blog_categories WHERE id = ?", (category_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'Blog category not found'}), 404
            
        return jsonify(dict(item))
    
    @app.route('/api/blog/categories', methods=['POST'])
    @token_required
    def create_blog_category(current_user):
        """
        Create a new blog category
        ---
        tags:
          - Blog
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
            description: Blog category created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO blog_categories (name) VALUES (?)",
            (data['name'],)
        )
        db.commit()
        
        return jsonify({'message': 'Blog category created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/blog/categories/<int:category_id>', methods=['PUT'])
    @token_required
    def update_blog_category(current_user, category_id):
        """
        Update a blog category
        ---
        tags:
          - Blog
        security:
          - Bearer: []
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the blog category
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
            description: Blog category updated
          400:
            description: Invalid input
          404:
            description: Blog category not found
        """
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists
        cur.execute("SELECT id FROM blog_categories WHERE id = ?", (category_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Blog category not found'}), 404
            
        # Update category
        cur.execute(
            "UPDATE blog_categories SET name = ? WHERE id = ?",
            (data['name'], category_id)
        )
        db.commit()
        
        return jsonify({'message': 'Blog category updated'})
    
    @app.route('/api/blog/categories/<int:category_id>', methods=['DELETE'])
    @token_required
    def delete_blog_category(current_user, category_id):
        """
        Soft delete a blog category
        ---
        tags:
          - Blog
        security:
          - Bearer: []
        parameters:
          - name: category_id
            in: path
            type: integer
            required: true
            description: ID of the blog category
        responses:
          200:
            description: Blog category deleted
          404:
            description: Blog category not found
          400:
            description: Cannot delete category with blog items
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists
        cur.execute("SELECT id FROM blog_categories WHERE id = ? AND is_deleted = 0", (category_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Blog category not found'}), 404

        # Check if category has blog items
        cur.execute("SELECT COUNT(*) as count FROM blog_items WHERE category_id = ? AND is_deleted = 0", (category_id,))
        count = cur.fetchone()['count']
        if count > 0:
            return jsonify({'message': 'Cannot delete category with blog items'}), 400
        
        # Soft delete category
        cur.execute("UPDATE blog_categories SET is_deleted = 1 WHERE id = ?", (category_id,))
        db.commit()
        
        return jsonify({'message': 'Blog category deleted'})
    
    # Blog Items
    @app.route('/api/blog/items', methods=['GET'])
    def get_blog_items():
        """
        Get all blog items
        ---
        tags:
          - Blog
        parameters:
          - name: category_id
            in: query
            type: integer
            required: false
            description: Filter by category ID
          - name: include_deleted
            in: query
            type: boolean
            required: false
            default: false
            description: Whether to include soft-deleted records
        responses:
          200:
            description: List of blog items
        """
        category_id = request.args.get('category_id')
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        db = get_db()
        cur = db.cursor()
        
        if category_id:
            if include_deleted:
                cur.execute("""
                    SELECT bi.*, bc.name as category_name 
                    FROM blog_items bi
                    LEFT JOIN blog_categories bc ON bi.category_id = bc.id
                    WHERE bi.category_id = ?
                    ORDER BY bi.date_time DESC
                """, (category_id,))
            else:
                cur.execute("""
                    SELECT bi.*, bc.name as category_name 
                    FROM blog_items bi
                    LEFT JOIN blog_categories bc ON bi.category_id = bc.id
                    WHERE bi.category_id = ? AND bi.is_deleted = 0 AND (bc.is_deleted = 0 OR bc.is_deleted IS NULL)
                    ORDER BY bi.date_time DESC
                """, (category_id,))
        else:
            if include_deleted:
                cur.execute("""
                    SELECT bi.*, bc.name as category_name 
                    FROM blog_items bi
                    LEFT JOIN blog_categories bc ON bi.category_id = bc.id
                    ORDER BY bi.date_time DESC
                """)
            else:
                cur.execute("""
                    SELECT bi.*, bc.name as category_name 
                    FROM blog_items bi
                    LEFT JOIN blog_categories bc ON bi.category_id = bc.id
                    WHERE bi.is_deleted = 0 AND (bc.is_deleted = 0 OR bc.is_deleted IS NULL)
                    ORDER BY bi.date_time DESC
                """)
            
        items = [dict(row) for row in cur.fetchall()]
        
        return jsonify(items)
    
    @app.route('/api/blog/items/<int:item_id>', methods=['GET'])
    def get_blog_item(item_id):
        """
        Get a specific blog item
        ---
        tags:
          - Blog
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the blog item
          - name: increment_views
            in: query
            type: boolean
            required: false
            description: Increment view count
        responses:
          200:
            description: Blog item details
          404:
            description: Blog item not found
        """
        increment_views = request.args.get('increment_views', 'false').lower() == 'true'
        
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            SELECT bi.*, bc.name as category_name 
            FROM blog_items bi
            LEFT JOIN blog_categories bc ON bi.category_id = bc.id
            WHERE bi.id = ?
        """, (item_id,))
        item = cur.fetchone()
        
        if not item:
            return jsonify({'message': 'Blog item not found'}), 404
            
        # Increment views if requested
        if increment_views:
            new_views = item['views'] + 1
            cur.execute("UPDATE blog_items SET views = ? WHERE id = ?", (new_views, item_id))
            db.commit()
            item = dict(item)
            item['views'] = new_views
            
        return jsonify(dict(item))
    
    @app.route('/api/blog/items', methods=['POST'])
    @token_required
    def create_blog_item(current_user):
        """
        Create a new blog item
        ---
        tags:
          - Blog
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
                img_or_video_link:
                  type: string
                text:
                  type: string
                intro_text:
                  type: string
        responses:
          201:
            description: Blog item created
          400:
            description: Invalid input
        """
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('text'):
            return jsonify({'message': 'Title and text are required'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if category exists if provided
        if data.get('category_id'):
            cur.execute("SELECT id FROM blog_categories WHERE id = ?", (data['category_id'],))
            if not cur.fetchone():
                return jsonify({'message': 'Blog category not found'}), 404
        
        now = datetime.datetime.now().isoformat()
        
        cur.execute(
            """INSERT INTO blog_items 
               (category_id, title, img_or_video_link, date_time, views, text, intro_text) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data.get('category_id'), data['title'], data.get('img_or_video_link'),
             now, 0, data['text'], data.get('intro_text'))
        )
        db.commit()
        
        return jsonify({'message': 'Blog item created', 'id': cur.lastrowid}), 201
    
    @app.route('/api/blog/items/<int:item_id>', methods=['PUT'])
    @token_required
    def update_blog_item(current_user, item_id):
        """
        Update a blog item
        ---
        tags:
          - Blog
        security:
          - Bearer: []
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the blog item
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
                img_or_video_link:
                  type: string
                text:
                  type: string
                intro_text:
                  type: string
        responses:
          200:
            description: Blog item updated
          400:
            description: Invalid input
          404:
            description: Blog item not found
        """
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if blog item exists
        cur.execute("SELECT id FROM blog_items WHERE id = ?", (item_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Blog item not found'}), 404
            
        # Check if category exists if provided
        if data.get('category_id'):
            cur.execute("SELECT id FROM blog_categories WHERE id = ?", (data['category_id'],))
            if not cur.fetchone():
                return jsonify({'message': 'Blog category not found'}), 404
        
        # Update blog item
        cur.execute(
            """UPDATE blog_items 
               SET category_id = ?, title = ?, img_or_video_link = ?, 
                   text = ?, intro_text = ? 
               WHERE id = ?""",
            (data.get('category_id'), data.get('title'), data.get('img_or_video_link'), 
             data.get('text'), data.get('intro_text'), item_id)
        )
        db.commit()
        
        return jsonify({'message': 'Blog item updated'})
    
    @app.route('/api/blog/items/<int:item_id>', methods=['DELETE'])
    @token_required
    def delete_blog_item(current_user, item_id):
        """
        Soft delete a blog item
        ---
        tags:
          - Blog
        security:
          - Bearer: []
        parameters:
          - name: item_id
            in: path
            type: integer
            required: true
            description: ID of the blog item
        responses:
          200:
            description: Blog item deleted
          404:
            description: Blog item not found
        """
        db = get_db()
        cur = db.cursor()
        
        # Check if blog item exists
        cur.execute("SELECT id FROM blog_items WHERE id = ? AND is_deleted = 0", (item_id,))
        if not cur.fetchone():
            return jsonify({'message': 'Blog item not found'}), 404
        
        # Soft delete blog item
        cur.execute("UPDATE blog_items SET is_deleted = 1 WHERE id = ?", (item_id,))
        db.commit()
        
        return jsonify({'message': 'Blog item deleted'})
