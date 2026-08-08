"""
Contractor Service
Business logic for contractor management, ratings, and work completion
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from fastapi import HTTPException, status

from app.models.contractor import ContractorProfile, ContractorRating, WorkCompletion, AvailabilityStatus
from app.models.user import User, UserRole
from app.models.issue import Issue, IssueStatus
from app.schemas.contractor import (
    ContractorProfileCreate,
    ContractorProfileUpdate,
    ContractorRatingCreate,
    WorkCompletionCreate,
    RatingBreakdown
)


class ContractorService:
    """Contractor management service"""
    
    @staticmethod
    def create_contractor_profile(
        contractor_data: ContractorProfileCreate,
        user_id: str,
        db: Session
    ) -> ContractorProfile:
        """
        Create a contractor profile for a user
        
        Args:
            contractor_data: Contractor profile creation data
            user_id: ID of the user (must have contractor role)
            db: Database session
            
        Returns:
            Created ContractorProfile
            
        Raises:
            HTTPException: If user not found, already has profile, or not a contractor
        """
        # Verify user exists and has contractor role
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.role != UserRole.CONTRACTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must have contractor role to create a contractor profile"
            )
        
        # Check if contractor profile already exists
        existing_profile = db.query(ContractorProfile).filter(
            ContractorProfile.user_id == user_id
        ).first()
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contractor profile already exists for this user"
            )
        
        # Check GST number uniqueness if provided
        if contractor_data.gst_number:
            existing_gst = db.query(ContractorProfile).filter(
                ContractorProfile.gst_number == contractor_data.gst_number
            ).first()
            if existing_gst:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="GST number already registered"
                )
        
        # Generate CONTCR-XXXXXX ID
        # Get the count of existing contractors to determine next number
        contractor_count = db.query(ContractorProfile).count()
        next_number = contractor_count + 1
        contractor_number = f"{next_number:06d}"  # Format as 000001, 000002, etc.
        contractor_id = f"CONTCR-{contractor_number}"
        
        # Check if ID already exists (race condition safety)
        while db.query(ContractorProfile).filter(ContractorProfile.id == contractor_id).first():
            next_number += 1
            contractor_number = f"{next_number:06d}"
            contractor_id = f"CONTCR-{contractor_number}"
        
        # Create contractor profile
        contractor_profile = ContractorProfile(
            id=contractor_id,
            user_id=user_id,
            company_name=contractor_data.company_name,
            gst_number=contractor_data.gst_number,
            license_number=contractor_data.license_number,
            specializations=contractor_data.specializations,
            years_of_experience=contractor_data.years_of_experience,
            is_available=True,
            availability_status=AvailabilityStatus.AVAILABLE,
            total_jobs_completed=0,
            average_rating=0.0,
            total_ratings=0,
            completion_rate=0.0,
            is_verified=False,
            is_active=True
        )
        
        db.add(contractor_profile)
        db.commit()
        db.refresh(contractor_profile)
        
        return contractor_profile
    
    @staticmethod
    def update_contractor_profile(
        contractor_id: str,
        contractor_data: ContractorProfileUpdate,
        db: Session
    ) -> ContractorProfile:
        """
        Update contractor profile
        
        Args:
            contractor_id: Contractor profile ID
            contractor_data: Updated contractor data
            db: Database session
            
        Returns:
            Updated ContractorProfile
            
        Raises:
            HTTPException: If contractor not found
        """
        contractor = db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if not contractor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contractor profile not found"
            )
        
        # Update fields if provided
        update_data = contractor_data.model_dump(exclude_unset=True)
        
        # Check GST uniqueness if being updated
        if "gst_number" in update_data and update_data["gst_number"]:
            existing_gst = db.query(ContractorProfile).filter(
                and_(
                    ContractorProfile.gst_number == update_data["gst_number"],
                    ContractorProfile.id != contractor_id
                )
            ).first()
            if existing_gst:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="GST number already registered"
                )
        
        # Handle availability status conversion
        if "availability_status" in update_data:
            try:
                update_data["availability_status"] = AvailabilityStatus(update_data["availability_status"])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid availability status. Must be one of: {[s.value for s in AvailabilityStatus]}"
                )
        
        for field, value in update_data.items():
            setattr(contractor, field, value)
        
        db.commit()
        db.refresh(contractor)
        
        return contractor
    
    @staticmethod
    def get_contractor_by_id(contractor_id: str, db: Session) -> ContractorProfile:
        """
        Get contractor profile by ID with user details
        
        Args:
            contractor_id: Contractor profile ID
            db: Database session
            
        Returns:
            ContractorProfile with user relationship loaded
            
        Raises:
            HTTPException: If contractor not found
        """
        contractor = db.query(ContractorProfile).options(
            joinedload(ContractorProfile.user)
        ).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if not contractor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contractor profile not found"
            )
        
        return contractor
    
    @staticmethod
    def get_contractor_by_user_id(user_id: str, db: Session) -> Optional[ContractorProfile]:
        """
        Get contractor profile by user ID
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            ContractorProfile or None if not found
        """
        return db.query(ContractorProfile).options(
            joinedload(ContractorProfile.user)
        ).filter(
            ContractorProfile.user_id == user_id
        ).first()
    
    @staticmethod
    def list_contractors(
        specialization: Optional[str] = None,
        is_available: Optional[bool] = None,
        min_rating: Optional[float] = None,
        is_verified: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
        db: Session = None
    ) -> tuple[List[ContractorProfile], int]:
        """
        List contractors with filters
        
        Args:
            specialization: Filter by specialization
            is_available: Filter by availability
            min_rating: Minimum average rating
            is_verified: Filter by verification status
            skip: Number of records to skip
            limit: Maximum number of records to return
            db: Database session
            
        Returns:
            Tuple of (contractors list, total count)
        """
        query = db.query(ContractorProfile).options(
            joinedload(ContractorProfile.user)
        ).filter(
            ContractorProfile.is_active == True
        )
        
        # Apply filters
        if specialization:
            # SQLite JSON query - check if specialization exists in array
            query = query.filter(
                ContractorProfile.specializations.contains(f'"{specialization}"')
            )
        
        if is_available is not None:
            query = query.filter(ContractorProfile.is_available == is_available)
        
        if min_rating is not None:
            query = query.filter(ContractorProfile.average_rating >= min_rating)
        
        if is_verified is not None:
            query = query.filter(ContractorProfile.is_verified == is_verified)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        contractors = query.offset(skip).limit(limit).all()
        
        return contractors, total
    
    @staticmethod
    def calculate_contractor_stats(contractor_id: str, db: Session) -> Dict[str, Any]:
        """
        Calculate comprehensive contractor statistics
        
        Args:
            contractor_id: Contractor profile ID
            db: Database session
            
        Returns:
            Dictionary with contractor statistics
            
        Raises:
            HTTPException: If contractor not found
        """
        contractor = ContractorService.get_contractor_by_id(contractor_id, db)
        
        # Get all completed work
        completed_work = db.query(WorkCompletion).filter(
            WorkCompletion.contractor_id == contractor_id
        ).all()
        
        # Get all ratings
        ratings = db.query(ContractorRating).filter(
            ContractorRating.contractor_id == contractor_id
        ).all()
        
        # Calculate rating breakdown
        rating_breakdown = RatingBreakdown()
        for rating in ratings:
            if rating.rating == 5:
                rating_breakdown.five_star += 1
            elif rating.rating == 4:
                rating_breakdown.four_star += 1
            elif rating.rating == 3:
                rating_breakdown.three_star += 1
            elif rating.rating == 2:
                rating_breakdown.two_star += 1
            elif rating.rating == 1:
                rating_breakdown.one_star += 1
        
        # Get jobs by category
        jobs_by_category = {}
        for work in completed_work:
            issue = db.query(Issue).filter(Issue.id == work.issue_id).first()
            if issue:
                category = issue.category.value
                jobs_by_category[category] = jobs_by_category.get(category, 0) + 1
        
        # Get recent ratings (last 5)
        recent_ratings = db.query(ContractorRating).options(
            joinedload(ContractorRating.reviewer)
        ).filter(
            ContractorRating.contractor_id == contractor_id
        ).order_by(
            ContractorRating.created_at.desc()
        ).limit(5).all()
        
        # Get total assigned jobs (including incomplete)
        total_assigned = db.query(Issue).filter(
            Issue.assigned_to == contractor.user_id
        ).count()
        
        # Calculate stats
        total_jobs = total_assigned
        completed_jobs = len(completed_work)
        cancelled_jobs = total_jobs - completed_jobs  # Simplified
        
        return {
            "contractor_id": contractor_id,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "cancelled_jobs": cancelled_jobs,
            "completion_rate": contractor.completion_rate,
            "average_rating": float(contractor.average_rating),
            "total_ratings": contractor.total_ratings,
            "rating_breakdown": rating_breakdown,
            "average_response_time_hours": contractor.response_time_avg,
            "jobs_by_category": jobs_by_category,
            "recent_ratings": recent_ratings
        }
    
    @staticmethod
    def verify_contractor(
        contractor_id: str,
        verified_by_user_id: str,
        db: Session
    ) -> ContractorProfile:
        """
        Verify a contractor (admin only)
        
        Args:
            contractor_id: Contractor profile ID
            verified_by_user_id: ID of admin user verifying
            db: Database session
            
        Returns:
            Updated ContractorProfile
        """
        contractor = ContractorService.get_contractor_by_id(contractor_id, db)
        
        contractor.is_verified = True
        contractor.verified_at = datetime.utcnow()
        contractor.verified_by = verified_by_user_id
        
        db.commit()
        db.refresh(contractor)
        
        return contractor


class RatingService:
    """Contractor rating service"""
    
    @staticmethod
    def create_rating(
        contractor_id: str,
        rating_data: ContractorRatingCreate,
        rated_by_user_id: str,
        db: Session
    ) -> ContractorRating:
        """
        Create a rating for a contractor
        
        Args:
            contractor_id: Contractor profile ID
            rating_data: Rating data
            rated_by_user_id: ID of user creating the rating
            db: Database session
            
        Returns:
            Created ContractorRating
            
        Raises:
            HTTPException: If validation fails
        """
        # Verify contractor exists
        contractor = ContractorService.get_contractor_by_id(contractor_id, db)
        
        # Verify issue exists and is assigned to this contractor
        issue = db.query(Issue).filter(Issue.id == rating_data.issue_id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        
        if issue.assigned_to != contractor.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Issue is not assigned to this contractor"
            )
        
        # Verify user is the issue reporter
        if issue.reported_by != rated_by_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the issue reporter can rate the contractor"
            )
        
        # Check for duplicate rating
        existing_rating = db.query(ContractorRating).filter(
            and_(
                ContractorRating.contractor_id == contractor_id,
                ContractorRating.issue_id == rating_data.issue_id
            )
        ).first()
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating already exists for this issue"
            )
        
        # Verify work is completed (optional - can be relaxed)
        work_completion = db.query(WorkCompletion).filter(
            WorkCompletion.issue_id == rating_data.issue_id
        ).first()
        if not work_completion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot rate contractor before work is marked as complete"
            )
        
        # Create rating
        rating = ContractorRating(
            contractor_id=contractor_id,
            issue_id=rating_data.issue_id,
            rated_by=rated_by_user_id,
            rating=rating_data.rating,
            quality_rating=rating_data.quality_rating,
            punctuality_rating=rating_data.punctuality_rating,
            professionalism_rating=rating_data.professionalism_rating,
            review_text=rating_data.review_text,
            work_photos=rating_data.work_photos
        )
        
        db.add(rating)
        
        # Update contractor's average rating
        RatingService._update_contractor_rating(contractor_id, db)
        
        db.commit()
        db.refresh(rating)
        
        return rating
    
    @staticmethod
    def _update_contractor_rating(contractor_id: str, db: Session):
        """
        Recalculate and update contractor's average rating
        
        Args:
            contractor_id: Contractor profile ID
            db: Database session
        """
        # Get all ratings for contractor
        ratings = db.query(ContractorRating).filter(
            ContractorRating.contractor_id == contractor_id
        ).all()
        
        if not ratings:
            return
        
        # Calculate average
        total_rating = sum(r.rating for r in ratings)
        average_rating = total_rating / len(ratings)
        
        # Update contractor profile
        contractor = db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if contractor:
            contractor.average_rating = round(average_rating, 2)
            contractor.total_ratings = len(ratings)
    
    @staticmethod
    def get_contractor_ratings(
        contractor_id: str,
        skip: int = 0,
        limit: int = 20,
        db: Session = None
    ) -> tuple[List[ContractorRating], int]:
        """
        Get ratings for a contractor
        
        Args:
            contractor_id: Contractor profile ID
            skip: Number of records to skip
            limit: Maximum number of records
            db: Database session
            
        Returns:
            Tuple of (ratings list, total count)
        """
        query = db.query(ContractorRating).options(
            joinedload(ContractorRating.reviewer)
        ).filter(
            ContractorRating.contractor_id == contractor_id
        ).order_by(
            ContractorRating.created_at.desc()
        )
        
        total = query.count()
        ratings = query.offset(skip).limit(limit).all()
        
        return ratings, total


class WorkCompletionService:
    """Work completion service"""
    
    @staticmethod
    def mark_work_complete(
        issue_id: str,
        completion_data: WorkCompletionCreate,
        contractor_user_id: str,
        db: Session
    ) -> WorkCompletion:
        """
        Mark work as complete for an issue
        
        Args:
            issue_id: Issue ID
            completion_data: Work completion data
            contractor_user_id: User ID of contractor (must be assigned)
            db: Database session
            
        Returns:
            Created WorkCompletion
            
        Raises:
            HTTPException: If validation fails
        """
        # Verify issue exists
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )
        
        # Verify contractor is assigned to this issue
        if issue.assigned_to != contractor_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned contractor can mark work as complete"
            )
        
        # Get contractor profile
        contractor_profile = ContractorService.get_contractor_by_user_id(contractor_user_id, db)
        if not contractor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contractor profile not found"
            )
        
        # Check for existing completion
        existing_completion = db.query(WorkCompletion).filter(
            WorkCompletion.issue_id == issue_id
        ).first()
        if existing_completion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Work completion already recorded for this issue"
            )
        
        # Get before photos from issue
        before_photos = [photo.photo_url for photo in issue.photos] if issue.photos else []
        
        # Generate WKCMP-XXXXXX ID
        completion_count = db.query(WorkCompletion).count()
        next_number = completion_count + 1
        completion_number = f"{next_number:06d}"
        completion_id = f"WKCMP-{completion_number}"
        
        # Check if ID already exists (race condition safety)
        while db.query(WorkCompletion).filter(WorkCompletion.id == completion_id).first():
            next_number += 1
            completion_number = f"{next_number:06d}"
            completion_id = f"WKCMP-{completion_number}"
        
        # Create work completion
        work_completion = WorkCompletion(
            id=completion_id,
            issue_id=issue_id,
            contractor_id=contractor_profile.id,
            completed_at=datetime.utcnow(),
            work_description=completion_data.work_description,
            materials_used=completion_data.materials_used,
            labor_cost=completion_data.labor_cost,
            total_cost=completion_data.total_cost,
            before_photos=before_photos,
            after_photos=completion_data.after_photos,
            is_verified=False
        )
        
        db.add(work_completion)
        
        # Update issue status to resolved
        issue.status = IssueStatus.RESOLVED
        issue.resolved_at = datetime.utcnow()
        
        # Update contractor metrics
        WorkCompletionService._update_contractor_metrics(contractor_profile.id, db)
        
        db.commit()
        db.refresh(work_completion)
        
        return work_completion
    
    @staticmethod
    def verify_work_completion(
        completion_id: str,
        is_approved: bool,
        verification_notes: Optional[str],
        verified_by_user_id: str,
        db: Session
    ) -> WorkCompletion:
        """
        Verify work completion (admin/facility role)
        
        Args:
            completion_id: Work completion ID
            is_approved: Whether work is approved
            verification_notes: Optional verification notes
            verified_by_user_id: ID of user verifying
            db: Database session
            
        Returns:
            Updated WorkCompletion
        """
        work_completion = db.query(WorkCompletion).filter(
            WorkCompletion.id == completion_id
        ).first()
        
        if not work_completion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work completion not found"
            )
        
        if work_completion.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Work completion already verified"
            )
        
        # Update verification
        work_completion.is_verified = is_approved
        work_completion.verified_at = datetime.utcnow()
        work_completion.verified_by = verified_by_user_id
        work_completion.verification_notes = verification_notes
        
        # If approved, update issue status to closed
        if is_approved:
            issue = db.query(Issue).filter(Issue.id == work_completion.issue_id).first()
            if issue:
                issue.status = IssueStatus.CLOSED
        
        db.commit()
        db.refresh(work_completion)
        
        return work_completion
    
    @staticmethod
    def _update_contractor_metrics(contractor_id: str, db: Session):
        """
        Update contractor performance metrics after work completion
        
        Args:
            contractor_id: Contractor profile ID
            db: Database session
        """
        contractor = db.query(ContractorProfile).filter(
            ContractorProfile.id == contractor_id
        ).first()
        
        if not contractor:
            return
        
        # Get completed work count
        completed_count = db.query(WorkCompletion).filter(
            WorkCompletion.contractor_id == contractor_id
        ).count()
        
        # Get total assigned issues
        total_assigned = db.query(Issue).filter(
            Issue.assigned_to == contractor.user_id
        ).count()
        
        # Update metrics
        contractor.total_jobs_completed = completed_count
        
        # Calculate completion rate
        if total_assigned > 0:
            completion_rate = (completed_count / total_assigned) * 100
            contractor.completion_rate = round(completion_rate, 2)
        
        db.commit()
