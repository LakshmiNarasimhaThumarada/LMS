async def create_indexes(db):
    """Create MongoDB indexes for optimal performance"""
    
    # PDF Analysis indexes
    await db.pdf_analysis.create_index([('user_id', 1), ('created_at', -1)])
    await db.pdf_analysis.create_index([('_id', 1), ('user_id', 1)])
    
    # Study Plans indexes
    await db.study_plans.create_index([('user_id', 1), ('status', 1)])
    await db.study_plans.create_index([('user_id', 1), ('created_at', -1)])
    await db.study_plans.create_index([('_id', 1), ('user_id', 1)])
    
    # Sessions index
    await db.study_plans.create_index([('sessions.date', 1)])
    
    # Calendar Credentials indexes
    await db.calendar_credentials.create_index([('user_id', 1), ('provider', 1)], unique=True)
    
    print("✅ Database indexes created")
