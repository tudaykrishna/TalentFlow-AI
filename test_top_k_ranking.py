"""
Test Script for Top-K Resume Ranking System

Run this after starting the backend to verify the changes work correctly.
"""

import requests
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api"
RECRUITER_ID = "test_recruiter_123"

def test_resume_screening():
    """Test the resume screening endpoint with top-K functionality"""
    
    print("=" * 60)
    print("Testing Top-K Resume Ranking System")
    print("=" * 60)
    
    # Test 1: Check if backend is running
    print("\n[Test 1] Checking backend connection...")
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/", timeout=5)
        print("✅ Backend is running")
    except Exception as e:
        print(f"❌ Backend is not running: {e}")
        print("Please start the backend first: python -m uvicorn Backend.main:app --reload")
        return
    
    # Test 2: Prepare test data
    print("\n[Test 2] Preparing test data...")
    jd_text = """
    Senior Python Developer
    
    We are looking for an experienced Python developer with:
    - 5+ years of Python development experience
    - Strong knowledge of FastAPI, Django, or Flask
    - Experience with machine learning and AI
    - Familiarity with Azure cloud services
    - Excellent problem-solving skills
    """
    
    print("✅ Test JD created")
    
    # Test 3: Check if test resumes exist
    print("\n[Test 3] Checking for test PDFs...")
    test_resume_dir = Path("resumes")
    
    if not test_resume_dir.exists():
        print("⚠️  No 'resumes' folder found in project root")
        print("Please add some PDF resumes to a 'resumes' folder to test")
        print("\nYou can still test with manual uploads through the Streamlit UI")
        return
    
    pdf_files = list(test_resume_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️  No PDF files found in 'resumes' folder")
        print("Please add some PDF resumes to test")
        return
    
    print(f"✅ Found {len(pdf_files)} PDF files")
    
    # Test 4: Screen resumes with different top_k values
    for top_k in [3, 5, len(pdf_files)]:
        print(f"\n[Test 4.{top_k}] Testing with top_k={top_k}...")
        
        if top_k > len(pdf_files):
            print(f"⚠️  Skipping (only {len(pdf_files)} files available)")
            continue
        
        # Prepare files for upload
        files = []
        for pdf_file in pdf_files[:10]:  # Limit to 10 for faster testing
            files.append(
                ('resumes', (pdf_file.name, open(pdf_file, 'rb'), 'application/pdf'))
            )
        
        data = {
            'recruiter_id': RECRUITER_ID,
            'jd_text': jd_text,
            'top_k': top_k
        }
        
        try:
            print(f"   Uploading {len(files)} resumes...")
            response = requests.post(
                f"{API_BASE_URL}/resume/screen",
                files=files,
                data=data,
                timeout=120
            )
            
            # Close file handles
            for _, (_, file_obj, _) in files:
                file_obj.close()
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   📊 Total uploaded: {result['total_uploaded']}")
                print(f"   ✅ Total processed: {result['total_processed']}")
                print(f"   🏆 Top candidates returned: {result['top_k']}")
                
                print(f"\n   Top {result['top_k']} Candidates:")
                for r in result['results']:
                    print(f"      #{r['rank']}: {r['candidate_name']} - {r['similarity_score']:.1f}% ({r['status']})")
                
                # Verify assertions
                assert len(result['results']) <= top_k, "❌ More results than top_k!"
                assert len(result['results']) > 0, "❌ No results returned!"
                
                # Check ranks are sequential
                ranks = [r['rank'] for r in result['results']]
                expected_ranks = list(range(1, len(result['results']) + 1))
                assert ranks == expected_ranks, f"❌ Ranks not sequential: {ranks}"
                
                # Check similarity scores are valid
                for r in result['results']:
                    assert 0 <= r['similarity_score'] <= 100, f"❌ Invalid score: {r['similarity_score']}"
                
                print(f"   ✅ All assertions passed!")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   {response.json()}")
                
        except requests.exceptions.Timeout:
            print("   ❌ Request timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 5: Retrieve results
    print("\n[Test 5] Retrieving screening history...")
    try:
        response = requests.get(f"{API_BASE_URL}/resume/results/{RECRUITER_ID}", timeout=5)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Found {len(results)} historical results")
            if results:
                latest = results[0]
                print(f"   Latest: {latest['candidate_name']} - {latest.get('similarity_score', latest.get('match_score', 0))}%")
        else:
            print(f"❌ Error retrieving results: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("1. Open Streamlit UI: streamlit run App/streamlit_app.py")
    print("2. Navigate to 'Resume Screener'")
    print("3. Upload PDFs and test the top-K slider")
    print("4. Verify the results match the API responses")

if __name__ == "__main__":
    test_resume_screening()
