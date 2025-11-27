#!/usr/bin/env python3
"""
CSV Processing Pipeline Test Runner
Runs comprehensive tests for the CSV upload and processing workflow.
"""

import sys
import os
import unittest
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import test modules
from tests.test_csv_pipeline import (
    TestCSVPreprocessor,
    TestGameValidator,
    TestCSVToDatabaseImporter,
    TestPipelineIntegration
)


class PipelineTestRunner:
    """Enhanced test runner with detailed reporting."""
    
    def __init__(self):
        self.test_suites = [
            ('CSV Preprocessor', TestCSVPreprocessor),
            ('Game Validator', TestGameValidator),
            ('CSV to Database Importer', TestCSVToDatabaseImporter),
            ('Pipeline Integration', TestPipelineIntegration)
        ]
        self.results = []
        
    def print_header(self):
        """Print test header."""
        print("\n" + "="*80)
        print(" "*20 + "CSV PROCESSING PIPELINE TESTS")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
    
    def print_suite_header(self, suite_name):
        """Print test suite header."""
        print(f"\n{'─'*80}")
        print(f"  Testing: {suite_name}")
        print(f"{'─'*80}")
    
    def run_suite(self, suite_name, test_class):
        """Run a single test suite."""
        self.print_suite_header(suite_name)
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        
        start_time = time.time()
        result = runner.run(suite)
        duration = time.time() - start_time
        
        self.results.append({
            'suite_name': suite_name,
            'result': result,
            'duration': duration
        })
        
        return result
    
    def print_suite_summary(self, suite_name, result, duration):
        """Print summary for a test suite."""
        total = result.testsRun
        passed = total - len(result.failures) - len(result.errors)
        failed = len(result.failures)
        errors = len(result.errors)
        
        status = "✓ PASSED" if result.wasSuccessful() else "✗ FAILED"
        
        print(f"\n  {suite_name} Summary:")
        print(f"    Status: {status}")
        print(f"    Tests run: {total}")
        print(f"    Passed: {passed}")
        print(f"    Failed: {failed}")
        print(f"    Errors: {errors}")
        print(f"    Duration: {duration:.2f}s")
    
    def print_final_summary(self):
        """Print final summary of all tests."""
        print("\n" + "="*80)
        print(" "*25 + "FINAL TEST SUMMARY")
        print("="*80)
        
        total_tests = sum(r['result'].testsRun for r in self.results)
        total_failures = sum(len(r['result'].failures) for r in self.results)
        total_errors = sum(len(r['result'].errors) for r in self.results)
        total_passed = total_tests - total_failures - total_errors
        total_duration = sum(r['duration'] for r in self.results)
        
        print(f"\n  Overall Statistics:")
        print(f"    Total test suites: {len(self.results)}")
        print(f"    Total tests run: {total_tests}")
        print(f"    Total passed: {total_passed} ({(total_passed/total_tests*100):.1f}%)")
        print(f"    Total failed: {total_failures}")
        print(f"    Total errors: {total_errors}")
        print(f"    Total duration: {total_duration:.2f}s")
        
        print("\n  Test Suites:")
        for result_data in self.results:
            suite_name = result_data['suite_name']
            result = result_data['result']
            duration = result_data['duration']
            
            status = "✓" if result.wasSuccessful() else "✗"
            passed = result.testsRun - len(result.failures) - len(result.errors)
            
            print(f"    {status} {suite_name}: {passed}/{result.testsRun} passed ({duration:.2f}s)")
        
        # Overall status
        all_passed = all(r['result'].wasSuccessful() for r in self.results)
        
        print("\n" + "="*80)
        if all_passed:
            print(" "*25 + "✓ ALL TESTS PASSED!")
            print(" "*20 + "Pipeline is ready for production!")
        else:
            print(" "*25 + "✗ SOME TESTS FAILED")
            print(" "*15 + "Please review the failures and fix them.")
        print("="*80)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        return all_passed
    
    def run_all(self):
        """Run all test suites."""
        self.print_header()
        
        for suite_name, test_class in self.test_suites:
            result = self.run_suite(suite_name, test_class)
            self.print_suite_summary(suite_name, result, self.results[-1]['duration'])
        
        all_passed = self.print_final_summary()
        
        return 0 if all_passed else 1


def main():
    """Main entry point."""
    runner = PipelineTestRunner()
    exit_code = runner.run_all()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

