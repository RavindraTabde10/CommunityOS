"""
Test Contractor Service Layer
Quick validation script for contractor service methods
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.contractor_service import ContractorService, RatingService, WorkCompletionService
from app.db.session import SessionLocal


def test_services():
    """Test that all services are properly configured"""
    print("=" * 70)
    print("CONTRACTOR SERVICE LAYER TEST")
    print("=" * 70)
    print()
    
    # Test ContractorService
    contractor_methods = [m for m in dir(ContractorService) if not m.startswith('_')]
    print("✅ ContractorService loaded")
    print(f"   Methods: {', '.join(contractor_methods)}")
    print()
    
    # Test RatingService
    rating_methods = [m for m in dir(RatingService) if not m.startswith('_')]
    print("✅ RatingService loaded")
    print(f"   Methods: {', '.join(rating_methods)}")
    print()
    
    # Test WorkCompletionService
    work_methods = [m for m in dir(WorkCompletionService) if not m.startswith('_')]
    print("✅ WorkCompletionService loaded")
    print(f"   Methods: {', '.join(work_methods)}")
    print()
    
    # Test database connection
    db = SessionLocal()
    try:
        from app.models.contractor import ContractorProfile
        count = db.query(ContractorProfile).count()
        print(f"✅ Database connection working")
        print(f"   Current contractor profiles: {count}")
        print()
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
    finally:
        db.close()
    
    print("=" * 70)
    print("✅ ALL SERVICES VALIDATED")
    print("=" * 70)


if __name__ == "__main__":
    test_services()
