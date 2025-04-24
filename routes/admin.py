from flask import jsonify, request
from werkzeug.security import generate_password_hash
import datetime

def register_admin_routes(app, get_db, token_required):
    
    @app.route('/api/admin/users', methods=['GET'])
    @token_required
    def get_admin_users(current_user):
        """
        Get all admin users
        ---
        tags:
          - Admin
        security:
          - Bearer: []
        responses:
          200:
            description: List of admin users
          403:
            description: Not authorized
        """
        # Only allow if current user has admin role
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Not authorized'}), 403
        
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, username, role, created_at, last_login FROM admin_users")
        users = [dict(row) for row in cur.fetchall()]
        
        return jsonify(users)
    
    @app.route('/api/admin/users/<int:user_id>', methods=['GET'])
    @token_required
    def get_admin_user(current_user, user_id):
        """
        Get a specific admin user
        ---
        tags:
          - Admin
        security:
          - Bearer: []
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: ID of the admin user
        responses:
          200:
            description: Admin user details
          403:
            description: Not authorized
          404:
            description: Admin user not found
        """
        # Only allow if current user has admin role
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Not authorized'}), 403
        
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, username, role, created_at, last_login FROM admin_users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        return jsonify(dict(user))
    
    @app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
    @token_required
    def update_admin_user(current_user, user_id):
        """
        Update an admin user
        ---
        tags:
          - Admin
        security:
          - Bearer: []
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: ID of the admin user
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
                role:
                  type: string
        responses:
          200:
            description: Admin user updated
          400:
            description: Invalid input
          403:
            description: Not authorized
          404:
            description: Admin user not found
        """
        # Only allow if current user has admin role
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Not authorized'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No input data provided'}), 400
            
        db = get_db()
        cur = db.cursor()
        
        # Check if user exists
        cur.execute("SELECT id FROM admin_users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            return jsonify({'message': 'User not found'}), 404
            
        # Update fields
        updates = []
        params = []
        
        if 'username' in data:
            updates.append("username = ?")
            params.append(data['username'])
            
        if 'password' in data:
            updates.append("password_hash = ?")
            params.append(generate_password_hash(data['password']))
            
        if 'role' in data:
            updates.append("role = ?")
            params.append(data['role'])
            
        if not updates:
            return jsonify({'message': 'No fields to update'}), 400
            
        # Add user_id to params
        params.append(user_id)
        
        # Execute update
        cur.execute(
            f"UPDATE admin_users SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        db.commit()
        
        return jsonify({'message': 'User updated'})
    
    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    @token_required
    def delete_admin_user(current_user, user_id):
        """
        Delete an admin user
        ---
        tags:
          - Admin
        security:
          - Bearer: []
        parameters:
          - name: user_id
            in: path
            type: integer
            required: true
            description: ID of the admin user
        responses:
          200:
            description: Admin user deleted
          403:
            description: Not authorized
          404:
            description: Admin user not found
        """
        # Only allow if current user has admin role
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Not authorized'}), 403
        
        # Prevent deleting yourself
        if current_user['id'] == user_id:
            return jsonify({'message': 'Cannot delete your own account'}), 400
        
        db = get_db()
        cur = db.cursor()
        
        # Check if user exists
        cur.execute("SELECT id FROM admin_users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            return jsonify({'message': 'User not found'}), 404
            
        # Delete user
        cur.execute("DELETE FROM admin_users WHERE id = ?", (user_id,))
        db.commit()
        
        return jsonify({'message': 'User deleted'})
