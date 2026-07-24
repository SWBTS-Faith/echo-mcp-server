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

async def get_prayer_by_id(prayer_id: int) -> Dict[str, Any]:
    """Get a specific prayer by its ID.
    
    Args:
        prayer_id: The ID of the prayer to retrieve
    
    Returns:
        The prayer details if found.
    """
    try:
        prayer = prayer_db.get_prayer_by_id(prayer_id)
        
        if not prayer:
            return {
                "success": False,
                "error": "Prayer not found"
            }
        
        return {
            "success": True,
            "prayer": {
                "id": prayer["id"],
                "title": prayer["prayer_title"],
                "description": prayer["prayer_description"],
                "steps": prayer["prayer_steps"],
                "category": prayer["feed_title"]
            }
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "get_prayer_by_id", "prayer_id": prayer_id})
        return {
            "success": False,
            "error": "Failed to retrieve prayer"
        }

async def get_prayers_by_category(feed_title: str, limit: int = 10) -> Dict[str, Any]:
    """Get prayers from a specific category.
    
    Args:
        feed_title: The category/feed title to filter by
        limit: Maximum number of prayers to return (default: 10)
    
    Returns:
        List of prayers from the specified category.
    """
    try:
        prayers = prayer_db.get_prayers_by_feed(feed_title, limit)
        
        if not prayers:
            return {
                "success": False,
                "error": f"No prayers found in category '{feed_title}'",
                "suggestion": "Check available categories with get_available_categories"
            }
        
        return {
            "success": True,
            "prayers": [
                {
                    "id": prayer["id"],
                    "title": prayer["prayer_title"],
                    "description": prayer["prayer_description"],
                    "steps": prayer["prayer_steps"],
                    "category": prayer["feed_title"]
                }
                for prayer in prayers
            ],
            "category": feed_title,
            "message": f"Found {len(prayers)} prayer(s) in '{feed_title}' category"
        }
        
    except Exception as e:
        log_error_with_context(e, {"operation": "get_prayers_by_category", "feed_title": feed_title})
        return {
            "success": False,
            "error": "Failed to retrieve prayers by category"
        }