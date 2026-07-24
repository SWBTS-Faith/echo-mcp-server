"""Echo Prayer MCP Server Tools - Readonly Database"""
import random
from typing import Dict, Any, Optional, List
from src.logging import logger, log_error_with_context
from src.prayer_db import prayer_db

# Encouraging messages for pray together tool
ENCOURAGEMENT_MESSAGES = [
    "You are not alone in your journey. God is with you every step of the way.",
    "Even in the darkest moments, there is hope and light ahead.",
    "Your prayers matter and are heard. Trust in God's perfect timing.",
    "Remember that God's love for you is unconditional and everlasting.",
    "Take comfort in knowing that others are praying for you too.",
    "God's grace is sufficient for all your needs.",
    "In times of struggle, remember that God is your refuge and strength.",
    "Your faith is a gift that will carry you through any storm.",
    "God sees your heart and knows your struggles. You are deeply loved.",
    "Trust in the Lord with all your heart, and lean not on your own understanding."
]

CONDOLENCE_MESSAGES = [
    "I'm deeply sorry for your loss. May God's peace comfort you during this difficult time.",
    "My heart goes out to you. May you find strength and comfort in God's love.",
    "In this time of grief, may you feel God's presence and the support of those who care about you.",
    "I'm praying for you and your family during this heartbreaking time.",
    "May God's grace surround you and bring you peace that surpasses understanding.",
    "Your loved one is now in God's loving arms. May you find comfort in that truth.",
    "I'm holding you in my prayers as you navigate this painful season.",
    "May God's love and the memories of your loved one bring you comfort.",
    "In this time of sorrow, may you feel God's gentle embrace.",
    "I'm here for you, and I'm praying that God will give you strength and peace."
]

ADVICE_MESSAGES = [
    "Take time to rest and care for yourself. God wants you to be well.",
    "Consider reaching out to a trusted friend or spiritual mentor for support.",
    "Remember that it's okay to not have all the answers. God is in control.",
    "Try to find moments of gratitude each day, even in difficult times.",
    "Don't be afraid to ask for help when you need it. God often works through others.",
    "Spend time in prayer and meditation. It can bring clarity and peace.",
    "Consider journaling your thoughts and feelings as a way to process what you're going through.",
    "Remember that healing takes time. Be patient and gentle with yourself.",
    "Focus on what you can control and trust God with the rest.",
    "Seek professional help if you're struggling with mental health. God wants you to be healthy."
]

async def one_minute_prayer() -> Dict[str, Any]:
    """Generate a one-minute prayer for quick spiritual connection.
    
    Returns:
        A random prayer from the database suitable for a quick prayer moment.
    """
    try:
        prayer = prayer_db.get_random_prayer()
        if not prayer:
            return {
                "success": False,
                "error": "No prayers available in the database"
            }
        
        return {
            "success": True,
            "prayer": {
                "title": prayer["prayer_title"],
                "description": prayer["prayer_description"],
                "steps": prayer["prayer_steps"],
                "category": prayer["feed_title"]
            },
            "message": "Here's a prayer to help you connect with God in this moment."
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "one_minute_prayer"})
        return {
            "success": False,
            "error": "Failed to generate prayer"
        }

async def guided_prayer_generator(query: str, feed_title: Optional[str] = None, limit: int = 3) -> Dict[str, Any]:
    """Generate guided prayers based on semantic search of the database.
    
    Args:
        query: Search query to find relevant prayers
        feed_title: Optional filter by specific prayer category
        limit: Maximum number of prayers to return (default: 3)
    
    Returns:
        List of relevant prayers based on the search query.
    """
    try:
        prayers = prayer_db.search_prayers_semantic(query, limit, feed_title)
        
        if not prayers:
            return {
                "success": False,
                "error": "No prayers found matching your query",
                "suggestion": "Try a different search term or browse available categories"
            }
        
        return {
            "success": True,
            "prayers": [
                {
                    "id": prayer["id"],
                    "title": prayer["prayer_title"],
                    "description": prayer["prayer_description"],
                    "steps": prayer["prayer_steps"],
                    "category": prayer["feed_title"],
                    "relevance_score": prayer["similarity_score"]
                }
                for prayer in prayers
            ],
            "query": query,
            "message": f"Found {len(prayers)} prayer(s) related to '{query}'"
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "guided_prayer_generator", "query": query})
        return {
            "success": False,
            "error": "Failed to search prayers"
        }

async def pray_together(message_type: str = "encouragement") -> Dict[str, Any]:
    """Provide encouragement, condolences, and advice for prayer support.
    
    Args:
        message_type: Type of message - "encouragement", "condolence", or "advice"
    
    Returns:
        A supportive message with prayer guidance.
    """
    try:
        if message_type == "encouragement":
            message = random.choice(ENCOURAGEMENT_MESSAGES)
            prayer_suggestion = "Consider praying for strength, hope, and God's presence in your life."
        elif message_type == "condolence":
            message = random.choice(CONDOLENCE_MESSAGES)
            prayer_suggestion = "Pray for peace, comfort, and healing during this time of loss."
        elif message_type == "advice":
            message = random.choice(ADVICE_MESSAGES)
            prayer_suggestion = "Pray for wisdom, guidance, and clarity in your decisions."
        else:
            message = random.choice(ENCOURAGEMENT_MESSAGES)
            prayer_suggestion = "Take a moment to pray and connect with God's love."
        
        return {
            "success": True,
            "message": message,
            "prayer_suggestion": prayer_suggestion,
            "type": message_type,
            "additional_support": "Remember that you're not alone. Others are praying for you too."
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "pray_together", "message_type": message_type})
        return {
            "success": False,
            "error": "Failed to generate supportive message"
        }

async def generate_prayer_request(topic: str, details: Optional[str] = None) -> Dict[str, Any]:
    """Generate a prayer request based on the topic and details provided.
    
    Args:
        topic: The main topic or situation for the prayer request
        details: Optional additional details about the situation
    
    Returns:
        A structured prayer request with suggested prayers from the database.
    """
    try:
        # Search for relevant prayers based on the topic
        search_query = f"{topic} {details or ''}".strip()
        prayers = prayer_db.search_prayers_semantic(search_query, limit=2)
        
        prayer_request = {
            "topic": topic,
            "details": details,
            "suggested_prayers": [],
            "prayer_points": [
                f"Pray for {topic.lower()}",
                "Ask for God's guidance and wisdom",
                "Seek peace and comfort",
                "Pray for strength and healing"
            ]
        }
        
        if prayers:
            prayer_request["suggested_prayers"] = [
                {
                    "title": prayer["prayer_title"],
                    "description": prayer["prayer_description"],
                    "category": prayer["feed_title"]
                }
                for prayer in prayers
            ]
        
        return {
            "success": True,
            "prayer_request": prayer_request,
            "message": f"Here's a prayer request for {topic}. Consider these prayer points and suggested prayers."
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "generate_prayer_request", "topic": topic})
        return {
            "success": False,
            "error": "Failed to generate prayer request"
        }

async def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """Authenticate a user with username and password.
    
    Args:
        username: User's username
        password: User's password
    
    Returns:
        Authentication result with access token if successful.
    """
    try:
        user = auth_manager.authenticate_user(username, password)
        
        if not user:
            return {
                "success": False,
                "error": "Invalid username or password"
            }
        
        # Create access token
        access_token = auth_manager.create_access_token(data={"sub": user["username"]})
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "authenticate_user", "username": username})
        return {
            "success": False,
            "error": "Authentication failed"
        }

async def create_user_account(username: str, password: str, email: Optional[str] = None) -> Dict[str, Any]:
    """Create a new user account.
    
    Args:
        username: Desired username
        password: User's password
        email: Optional email address
    
    Returns:
        Account creation result.
    """
    try:
        result = auth_manager.create_user(username, password, email)
        return result
        
    except Exception as e:
        log_error_with_context(e, {"operation": "create_user_account", "username": username})
        return {
            "success": False,
            "error": "Failed to create account"
        }

async def share_prayer(token: str, prayer_id: int, share_type: str, 
                      shared_with_user_id: Optional[int] = None, 
                      shared_with_group: Optional[str] = None) -> Dict[str, Any]:
    """Share a prayer with another user or group (requires authentication).
    
    Args:
        token: User's authentication token
        prayer_id: ID of the prayer to share
        share_type: "private" or "public"
        shared_with_user_id: ID of user to share with (for private shares)
        shared_with_group: Group name to share with (for public shares)
    
    Returns:
        Share operation result.
    """
    try:
        # Verify authentication
        user = auth_manager.verify_token(token)
        if not user:
            return {
                "success": False,
                "error": "Invalid or expired authentication token"
            }
        
        # Verify prayer exists
        prayer = prayer_db.get_prayer_by_id(prayer_id)
        if not prayer:
            return {
                "success": False,
                "error": "Prayer not found"
            }
        
        # Share the prayer
        result = auth_manager.share_prayer(
            user["id"], prayer_id, share_type, shared_with_user_id, shared_with_group
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Prayer '{prayer['prayer_title']}' shared successfully",
                "share_id": result["share_id"]
            }
        else:
            return result
        
    except Exception as e:
        log_error_with_context(e, {"operation": "share_prayer", "prayer_id": prayer_id})
        return {
            "success": False,
            "error": "Failed to share prayer"
        }

async def get_group_prayers(token: str, group_name: Optional[str] = None) -> Dict[str, Any]:
    """Access prayers from a certain group (requires authentication).
    
    Args:
        token: User's authentication token
        group_name: Optional specific group name to filter by
    
    Returns:
        List of prayers shared with the user or in public groups.
    """
    try:
        # Verify authentication
        user = auth_manager.verify_token(token)
        if not user:
            return {
                "success": False,
                "error": "Invalid or expired authentication token"
            }
        
        # Get prayers shared with user
        shared_prayers = auth_manager.get_prayers_shared_with_user(user["id"])
        
        # Filter by group if specified
        if group_name:
            shared_prayers = [p for p in shared_prayers if p["shared_with_group"] == group_name]
        
        # Get prayer details for each share
        prayers_with_details = []
        for share in shared_prayers:
            prayer = prayer_db.get_prayer_by_id(share["prayer_id"])
            if prayer:
                prayers_with_details.append({
                    "share_id": share["share_id"],
                    "prayer": prayer,
                    "shared_by": share["shared_by_username"],
                    "shared_at": share["created_at"],
                    "share_type": share["share_type"],
                    "group": share["shared_with_group"]
                })
        
        return {
            "success": True,
            "prayers": prayers_with_details,
            "group_filter": group_name,
            "message": f"Found {len(prayers_with_details)} prayer(s) shared with you"
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "get_group_prayers"})
        return {
            "success": False,
            "error": "Failed to retrieve group prayers"
        }

async def list_user_shared_prayers(token: str) -> Dict[str, Any]:
    """List all prayers that were shared by the user (requires authentication).
    
    Args:
        token: User's authentication token
    
    Returns:
        List of prayers shared by the authenticated user.
    """
    try:
        # Verify authentication
        user = auth_manager.verify_token(token)
        if not user:
            return {
                "success": False,
                "error": "Invalid or expired authentication token"
            }
        
        # Get prayers shared by user
        user_shares = auth_manager.get_user_shared_prayers(user["id"])
        
        # Get prayer details for each share
        prayers_with_details = []
        for share in user_shares:
            prayer = prayer_db.get_prayer_by_id(share["prayer_id"])
            if prayer:
                prayers_with_details.append({
                    "share_id": share["share_id"],
                    "prayer": prayer,
                    "shared_with": share["shared_with_username"] or share["shared_with_group"],
                    "shared_at": share["created_at"],
                    "share_type": share["share_type"]
                })
        
        return {
            "success": True,
            "prayers": prayers_with_details,
            "message": f"You have shared {len(prayers_with_details)} prayer(s)"
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "list_user_shared_prayers"})
        return {
            "success": False,
            "error": "Failed to retrieve your shared prayers"
        }

async def list_prayers_shared_with_user(token: str) -> Dict[str, Any]:
    """List all prayers that are shared to the user (requires authentication).
    
    Args:
        token: User's authentication token
    
    Returns:
        List of prayers shared with the authenticated user.
    """
    try:
        # Verify authentication
        user = auth_manager.verify_token(token)
        if not user:
            return {
                "success": False,
                "error": "Invalid or expired authentication token"
            }
        
        # Get prayers shared with user
        shared_prayers = auth_manager.get_prayers_shared_with_user(user["id"])
        
        # Get prayer details for each share
        prayers_with_details = []
        for share in shared_prayers:
            prayer = prayer_db.get_prayer_by_id(share["prayer_id"])
            if prayer:
                prayers_with_details.append({
                    "share_id": share["share_id"],
                    "prayer": prayer,
                    "shared_by": share["shared_by_username"],
                    "shared_at": share["created_at"],
                    "share_type": share["share_type"],
                    "group": share["shared_with_group"]
                })
        
        return {
            "success": True,
            "prayers": prayers_with_details,
            "message": f"You have {len(prayers_with_details)} prayer(s) shared with you"
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "list_prayers_shared_with_user"})
        return {
            "success": False,
            "error": "Failed to retrieve prayers shared with you"
        }

async def get_available_categories() -> Dict[str, Any]:
    """Get all available prayer categories/feed titles.
    
    Returns:
        List of available prayer categories.
    """
    try:
        categories = prayer_db.get_feed_titles()
        
        return {
            "success": True,
            "categories": categories,
            "message": f"Found {len(categories)} prayer categories available"
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "get_available_categories"})
        return {
            "success": False,
            "error": "Failed to retrieve categories"
        }