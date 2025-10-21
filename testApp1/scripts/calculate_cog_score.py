#!/usr/bin/env python3
"""
Cognitive Score Calculator CLI
Standalone script to calculate cognitive scores from basketball CSV files.

Usage:
    python calculate_cog_score.py <csv_file> [options]
    
Options:
    --json <output_file>    Save results as JSON
    --print                 Print formatted report (default)
    
Examples:
    python calculate_cog_score.py game_data.csv
    python calculate_cog_score.py game_data.csv --json report.json
"""

import sys
import os
import argparse

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.processors.cog_score_calculator import CogScoreCalculator


def main():
    parser = argparse.ArgumentParser(
        description='Calculate cognitive scores from basketball game CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ../10.06.25\ Heat\ v\ Bucks\ \(1\).csv
  %(prog)s game_data.csv --json output.json
  %(prog)s game_data.csv --json output.json --print
        """
    )
    
    parser.add_argument(
        'csv_file',
        help='Path to CSV file containing game data'
    )
    
    parser.add_argument(
        '--json',
        dest='json_output',
        metavar='FILE',
        help='Save results as JSON to specified file'
    )
    
    parser.add_argument(
        '--print',
        dest='print_report',
        action='store_true',
        default=True,
        help='Print formatted report to console (default: True)'
    )
    
    parser.add_argument(
        '--no-print',
        dest='print_report',
        action='store_false',
        help='Do not print report to console'
    )
    
    args = parser.parse_args()
    
    # Verify file exists
    if not os.path.exists(args.csv_file):
        print(f"Error: File not found: {args.csv_file}", file=sys.stderr)
        sys.exit(1)
    
    # Create calculator instance
    try:
        calculator = CogScoreCalculator(args.csv_file)
        
        # Print report if requested
        if args.print_report:
            calculator.print_report()
        
        # Save JSON if requested
        if args.json_output:
            calculator.save_report_json(args.json_output)
            if not args.print_report:
                print(f"✓ Report saved to: {args.json_output}")
        
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

