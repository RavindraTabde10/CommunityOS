"""
API Router - Version 1
Aggregates all API endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, issues, photos, users, comments, contractors, work_completions, assets, bookings, reports, announcements, committee, feedback, visitors, guidelines, water_tanker
from app.api.v1 import events, polls

api_router = APIRouter()

# Active endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(issues.router, prefix="/issues", tags=["Issues"])
api_router.include_router(comments.router, prefix="/issues", tags=["Comments & Activity"])
api_router.include_router(photos.router, tags=["Photos"])
api_router.include_router(contractors.router, prefix="/contractors", tags=["Contractors"])
api_router.include_router(work_completions.router, prefix="/work-completions", tags=["Work Completions"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets & Facilities"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports & Analytics"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["Announcements"])
api_router.include_router(committee.router, prefix="/committee", tags=["Committee"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(polls.router, prefix="/polls", tags=["Polls"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(visitors.router, prefix="/visitors", tags=["Visitors"])
api_router.include_router(guidelines.router, prefix="/guidelines", tags=["Security Guidelines"])
api_router.include_router(water_tanker.router, prefix="/water-tanker", tags=["Water Tanker"])


@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Riverdale Connect API v1",
        "docs": "/api/docs"
    }
