"""
Contractor API Endpoints Test
Quick validation of all contractor endpoints
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.main import app
from fastapi.openapi.utils import get_openapi


def test_contractor_endpoints():
    """Test that all contractor endpoints are registered"""
    print("=" * 70)
    print("CONTRACTOR API ENDPOINTS TEST")
    print("=" * 70)
    print()
    
    # Get OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes
    )
    
    # Total endpoints
    total_endpoints = len(openapi_schema['paths'])
    print(f"✅ Total API endpoints: {total_endpoints}")
    print()
    
    # Contractor endpoints
    contractor_paths = [
        p for p in openapi_schema['paths'].keys() 
        if 'contractor' in p or 'work-completion' in p or 'assign' in p or 'complete' in p
    ]
    
    print(f"✅ Contractor-related endpoints: {len(contractor_paths)}")
    print()
    
    # List all contractor endpoints with methods
    print("Contractor Endpoints by Category:")
    print()
    
    print("📋 Contractor Profile Management:")
    profile_endpoints = [p for p in contractor_paths if p.startswith('/api/v1/contractors')]
    for path in sorted(profile_endpoints):
        methods = list(openapi_schema['paths'][path].keys())
        methods = [m.upper() for m in methods if m != 'parameters']
        print(f"  {', '.join(methods):15} {path}")
    print()
    
    print("📋 Issue Assignment & Work Completion:")
    issue_endpoints = [p for p in contractor_paths if '/issues/' in p]
    for path in sorted(issue_endpoints):
        methods = list(openapi_schema['paths'][path].keys())
        methods = [m.upper() for m in methods if m != 'parameters']
        print(f"  {', '.join(methods):15} {path}")
    print()
    
    print("📋 Work Verification:")
    work_endpoints = [p for p in contractor_paths if '/work-completion' in p]
    for path in sorted(work_endpoints):
        methods = list(openapi_schema['paths'][path].keys())
        methods = [m.upper() for m in methods if m != 'parameters']
        print(f"  {', '.join(methods):15} {path}")
    print()
    
    # Verify expected endpoints exist
    expected_endpoints = [
        "/api/v1/contractors/",
        "/api/v1/contractors/{contractor_id}",
        "/api/v1/contractors/{contractor_id}/stats",
        "/api/v1/contractors/{contractor_id}/verify",
        "/api/v1/contractors/{contractor_id}/rate",
        "/api/v1/contractors/{contractor_id}/ratings",
        "/api/v1/issues/{issue_id}/assign",
        "/api/v1/issues/{issue_id}/complete",
        "/api/v1/work-completions/{completion_id}/verify"
    ]
    
    print("Validation:")
    all_present = True
    for endpoint in expected_endpoints:
        if endpoint in contractor_paths:
            print(f"  ✅ {endpoint}")
        else:
            print(f"  ❌ {endpoint} - MISSING!")
            all_present = False
    print()
    
    if all_present:
        print("=" * 70)
        print("✅ ALL CONTRACTOR ENDPOINTS VALIDATED")
        print("=" * 70)
    else:
        print("=" * 70)
        print("❌ SOME ENDPOINTS MISSING")
        print("=" * 70)
    
    print()
    print("🚀 Ready to test!")
    print("   Start server: uvicorn app.main:app --reload")
    print("   View docs: http://127.0.0.1:8000/api/docs")


if __name__ == "__main__":
    test_contractor_endpoints()
