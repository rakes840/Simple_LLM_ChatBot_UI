def authenticate_user(username, password):
    """Authenticate a user."""
    try:
        if not username or not password:
            return None
        
        with get_db() as db:
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                logger.info(f"Authentication attempt for non-existent user: {username}")
                return None
            
            if not verify_password(user.hashed_password, password):
                logger.info(f"Failed authentication for user: {username}")
                return None
            
            # Update last login time and login count
            user.last_login = datetime.utcnow()
            user.login_count += 1
            db.commit()
            
            # Create a dictionary with user data to avoid detached instance issues
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login,
                'login_count': user.login_count
            }
            
            logger.info(f"Successful authentication for user: {username}")
            return user_data  # Return dictionary instead of SQLAlchemy object
    
    except SQLAlchemyError as e:
        logger.error(f"Database error in authenticate_user: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return None
    except Exception as e:
        logger.error(f"Error in authenticate_user: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return None





if user:
    logger.info(f"User '{user['username']}' logged in successfully")
    st.session_state.user_id = user['id']
    st.session_state.username = user['username']
    st.session_state.authenticated = True
    st.session_state.login_attempts = 0  # Reset login attempts
    st.success(f"Welcome back, {user['username']}!")
    time.sleep(1)
    st.rerun()


