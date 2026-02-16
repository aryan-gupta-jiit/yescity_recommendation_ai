"""
Test script to verify the parser works correctly
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from yescity_recommendation_ai.crew.crew_output_parser import CrewOutputParser

# Test case 1: Well-formatted JSON
test_output_1 = '''{
    "recommendations": [
        {"_id": "68c7f27e20f4dc4834768b6d", "shops": "JDS Banaras"},
        {"_id": "68c7f27e20f4dc4834768b6e", "shops": "ALBELI"}
    ]
}'''

# Test case 2: JSON with extra whitespace /newlines (like Ollama output)
test_output_2 = '''
{
    "recommendations": [
        {
            "_id": "68c7f27e20f4dc4834768b6d",
            "shops": "JDS Banaras"
        },
        {
            "_id": "68c7f27e20f4dc4834768b6e",
            "shops": "ALBELI Shop"
        }
    ]
}
'''

# Test case 3: JSON with surrounding text
test_output_3 = '''Here are the recommendations:
{
    "recommendations": [
        {"_id": "test123", "shops": "Test Shop"}
    ]
}
That's all!'''

print("=" * 60)
print("Test Case 1: Well-formatted JSON")
print("=" * 60)
result1 = CrewOutputParser.parse_shopping_recommendations(test_output_1)
print(f"Result: {result1}")
print(f"Success: {len(result1) > 0}")
print()

print("=" * 60)
print("Test Case 2: JSON with extra whitespace")
print("=" * 60)
result2 = CrewOutputParser.parse_shopping_recommendations(test_output_2)
print(f"Result: {result2}")
print(f"Success: {len(result2) > 0}")
print()

print("=" * 60)
print("Test Case 3: JSON with surrounding text")
print("=" * 60)
result3 = CrewOutputParser.parse_shopping_recommendations(test_output_3)
print(f"Result: {result3}")
print(f"Success: {len(result3) > 0}")
print()

print("=" * 60)
print("Summary")
print("=" * 60)
print(f"Test 1: {'✅ PASS' if len(result1) == 2 else '❌ FAIL'}")
print(f"Test 2: {'✅ PASS' if len(result2) == 2 else '❌ FAIL'}")
print(f"Test 3: {'✅ PASS' if len(result3) == 1 else '❌ FAIL'}")
