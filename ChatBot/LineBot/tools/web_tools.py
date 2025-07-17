from LineBot.models import User_Info
import json

def get_user_statistics(user_id: str) -> str:
    """Get statistics about user's interactions"""
    try:
        total_messages = User_Info.objects.filter(uid=user_id).count()
        first_message = User_Info.objects.filter(uid=user_id).first()
        last_message = User_Info.objects.filter(uid=user_id).last()
        
        stats = {
            "total_messages": total_messages,
            "first_interaction": str(first_message.mdt) if first_message else None,
            "last_interaction": str(last_message.mdt) if last_message else None
        }
        
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error getting statistics: {str(e)}"

def save_note(user_id: str, note: str) -> str:
    """Save a note for the user"""
    try:
        User_Info.objects.create(
            uid=user_id,
            name="Web User",
            pic_url="",
            mtext=f"[NOTE] {note}",
        )
        return "Note saved successfully"
    except Exception as e:
        return f"Error saving note: {str(e)}"