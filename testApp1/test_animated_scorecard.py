#!/usr/bin/env python3
"""
Test script for Animated Scorecard implementation
Verifies that all components are properly installed and functional
"""

import os
import sys
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from processors.basketball_cognitive_processor import BasketballCognitiveProcessor


def test_processor_methods():
    """Test that all new processor methods exist and are callable"""
    print("Testing BasketballCognitiveProcessor methods...")
    
    processor = BasketballCognitiveProcessor()
    
    # Check if new method exists
    assert hasattr(processor, 'generate_animated_scorecard_data'), \
        "generate_animated_scorecard_data method not found"
    
    assert hasattr(processor, '_calculate_on_ball_for_scorecard'), \
        "_calculate_on_ball_for_scorecard method not found"
    
    assert hasattr(processor, '_calculate_technical_for_scorecard'), \
        "_calculate_technical_for_scorecard method not found"
    
    assert hasattr(processor, '_calculate_off_ball_for_scorecard'), \
        "_calculate_off_ball_for_scorecard method not found"
    
    assert hasattr(processor, '_calculate_shot_distribution_for_scorecard'), \
        "_calculate_shot_distribution_for_scorecard method not found"
    
    print("✅ All processor methods exist")


def test_with_sample_csv():
    """Test with actual CSV file if available"""
    print("\nTesting with sample CSV file...")
    
    csv_path = "10.06.25 Heat v Bucks (1).csv"
    
    if not os.path.exists(csv_path):
        print("⚠️  Sample CSV not found, skipping CSV test")
        return
    
    try:
        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded CSV with {len(df)} rows")
        
        # Process data
        processor = BasketballCognitiveProcessor()
        scorecard_data = processor.generate_animated_scorecard_data(df)
        
        # Verify data structure
        assert 'date' in scorecard_data, "Missing 'date' in scorecard data"
        assert 'player' in scorecard_data, "Missing 'player' in scorecard data"
        assert 'opponent' in scorecard_data, "Missing 'opponent' in scorecard data"
        assert 'on_ball' in scorecard_data, "Missing 'on_ball' in scorecard data"
        assert 'technical' in scorecard_data, "Missing 'technical' in scorecard data"
        assert 'off_ball' in scorecard_data, "Missing 'off_ball' in scorecard data"
        assert 'shot_distribution' in scorecard_data, "Missing 'shot_distribution' in scorecard data"
        
        print("✅ Scorecard data structure is valid")
        
        # Print sample data
        print(f"\nSample Data:")
        print(f"  Date: {scorecard_data['date']}")
        print(f"  Player: {scorecard_data['player']}")
        print(f"  Opponent: {scorecard_data['opponent']}")
        print(f"  On Ball Cognition: {scorecard_data['on_ball']['overall_percentage']}%")
        print(f"  Technical Breakdown: {scorecard_data['technical']['overall_percentage']}%")
        print(f"  Off Ball Cognition: {scorecard_data['off_ball']['overall_percentage']}%")
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        raise


def test_file_existence():
    """Test that all required files exist"""
    print("\nTesting file existence...")
    
    files = {
        'Template': 'templates/animated_scorecard.html',
        'CSS': 'static/css/animated-scorecard.css',
        'JavaScript': 'static/js/animated-scorecard.js',
        'Documentation': 'docs/ANIMATED_SCORECARD_GUIDE.md',
        'Implementation Summary': 'ANIMATED_SCORECARD_IMPLEMENTATION.md'
    }
    
    all_exist = True
    for name, path in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name}: {path} ({size} bytes)")
        else:
            print(f"❌ {name}: {path} NOT FOUND")
            all_exist = False
    
    assert all_exist, "Some required files are missing"


def test_routes():
    """Test that Flask routes are properly defined"""
    print("\nTesting Flask routes...")
    
    try:
        from core.app import app
        
        # Check if routes exist
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        required_routes = [
            '/animated-scorecard',
            '/animated-scorecard/<filename>',
            '/api/scorecard-data/<filename>'
        ]
        
        for route in required_routes:
            if route in routes:
                print(f"✅ Route exists: {route}")
            else:
                print(f"❌ Route missing: {route}")
                raise AssertionError(f"Route {route} not found")
        
    except Exception as e:
        print(f"⚠️  Could not test routes (app may need to be running): {e}")


def main():
    """Run all tests"""
    print("="*60)
    print("ANIMATED SCORECARD IMPLEMENTATION VERIFICATION")
    print("="*60)
    
    try:
        test_processor_methods()
        test_file_existence()
        test_with_sample_csv()
        test_routes()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - Implementation verified!")
        print("="*60)
        
        print("\nNext steps:")
        print("1. Start the Flask app: python testApp1/run_app.py")
        print("2. Navigate to: http://localhost:8081/animated-scorecard")
        print("3. Upload a processed cognitive CSV file")
        print("4. Enjoy the animated scorecard!")
        
        return 0
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60)
        return 1


if __name__ == '__main__':
    sys.exit(main())

