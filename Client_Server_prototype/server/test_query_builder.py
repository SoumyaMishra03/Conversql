"""
Enhanced test script to validate all query builders with detailed failure analysis
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Query_Builder.query_builder_factory import build_query
from Query_Builder.test_queries import ALL_TEST_QUERIES

class TestResults:
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.total_passed = 0
        self.total_failed = 0
        self.total_errors = 0

    def add_result(self, query_type, test_name, status, error_msg=None, details=None):
        if query_type not in self.results:
            self.results[query_type] = {
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'total': 0,
                'details': []
            }
        
        self.results[query_type]['total'] += 1
        self.results[query_type]['details'].append({
            'test': test_name,
            'status': status,
            'error': error_msg,
            'details': details
        })
        
        if status == 'PASS':
            self.results[query_type]['passed'] += 1
            self.total_passed += 1
        elif status == 'FAIL':
            self.results[query_type]['failed'] += 1
            self.total_failed += 1
        elif status == 'ERROR':
            self.results[query_type]['errors'] += 1
            self.total_errors += 1
        
        self.total_tests += 1

    def get_accuracy(self, query_type=None):
        if query_type:
            if query_type in self.results:
                total = self.results[query_type]['total']
                passed = self.results[query_type]['passed']
                return (passed / total * 100) if total > 0 else 0
            return 0
        else:
            return (self.total_passed / self.total_tests * 100) if self.total_tests > 0 else 0

    def print_summary(self):
        print(f"\n{'='*80}")
        print("QUERY BUILDER TEST RESULTS SUMMARY")
        print(f"{'='*80}")
        
        # Individual query type results
        for query_type, results in self.results.items():
            accuracy = self.get_accuracy(query_type)
            print(f"\n{query_type} Query Builder:")
            print(f"  Total Tests: {results['total']}")
            print(f"  ✅ Passed: {results['passed']}")
            print(f"  ❌ Failed: {results['failed']}")
            print(f"  🚫 Errors: {results['errors']}")
            print(f"  📊 Accuracy: {accuracy:.1f}%")
            
            # Show failed/error details with enhanced information
            if results['failed'] > 0 or results['errors'] > 0:
                print(f"  Issues:")
                for detail in results['details']:
                    if detail['status'] in ['FAIL', 'ERROR']:
                        status_icon = "❌" if detail['status'] == 'FAIL' else "🚫"
                        print(f"    {status_icon} {detail['test']}")
                        if detail['error']:
                            print(f"       Error: {detail['error']}")
                        if detail['details']:
                            for key, value in detail['details'].items():
                                print(f"       {key}: {value}")
        
        # Overall results
        overall_accuracy = self.get_accuracy()
        print(f"\n{'='*80}")
        print("OVERALL RESULTS:")
        print(f"  Total Tests: {self.total_tests}")
        print(f"  ✅ Passed: {self.total_passed}")
        print(f"  ❌ Failed: {self.total_failed}")
        print(f"  🚫 Errors: {self.total_errors}")
        print(f"  📊 Overall Accuracy: {overall_accuracy:.1f}%")
        print(f"{'='*80}")
        
        # Performance rating
        if overall_accuracy >= 90:
            print("🎉 EXCELLENT - Query builders are performing very well!")
        elif overall_accuracy >= 75:
            print("👍 GOOD - Query builders are working well with minor issues")
        elif overall_accuracy >= 50:
            print("⚠️  FAIR - Query builders need some improvements")
        else:
            print("🔧 NEEDS WORK - Query builders require significant fixes")

def analyze_failure(expected_pattern, generated_query):
    """Analyze why a test failed with detailed comparison"""
    analysis = {}
    
    # Basic length comparison
    analysis['Expected Length'] = len(expected_pattern)
    analysis['Generated Length'] = len(generated_query)
    
    # Case sensitivity check
    if expected_pattern.lower() == generated_query.lower():
        analysis['Issue'] = "Case sensitivity mismatch"
        return analysis
    
    # Check if pattern exists anywhere in query
    if expected_pattern in generated_query:
        analysis['Issue'] = "Pattern found but test logic error"
        return analysis
    
    # Check if it's a substring issue
    if expected_pattern.lower() in generated_query.lower():
        analysis['Issue'] = "Pattern found with case differences"
        return analysis
    
    # Find first difference
    min_len = min(len(expected_pattern), len(generated_query))
    first_diff = -1
    for i in range(min_len):
        if expected_pattern[i] != generated_query[i]:
            first_diff = i
            break
    
    if first_diff >= 0:
        analysis['First Difference At'] = f"Position {first_diff}"
        analysis['Expected Char'] = f"'{expected_pattern[first_diff]}'"
        analysis['Generated Char'] = f"'{generated_query[first_diff]}'"
        analysis['Context Expected'] = f"...{expected_pattern[max(0,first_diff-10):first_diff+10]}..."
        analysis['Context Generated'] = f"...{generated_query[max(0,first_diff-10):first_diff+10]}..."
    
    # Check for common issues
    if '`' in expected_pattern and '`' not in generated_query:
        analysis['Issue'] = "Missing backticks in generated query"
    elif 'WHERE' in expected_pattern and 'WHERE' not in generated_query:
        analysis['Issue'] = "Missing WHERE clause"
    elif 'SET' in expected_pattern and 'SET' not in generated_query:
        analysis['Issue'] = "Missing SET clause"
    elif 'INSERT INTO' in expected_pattern and 'INSERT INTO' not in generated_query:
        analysis['Issue'] = "Missing INSERT INTO clause"
    elif 'DELETE FROM' in expected_pattern and 'DELETE FROM' not in generated_query:
        analysis['Issue'] = "Missing DELETE FROM clause"
    else:
        analysis['Issue'] = "Structural difference in SQL generation"
    
    return analysis

def test_query_builder(query_type, test_queries, test_results):
    """Test a specific query builder with its test queries"""
    print(f"\n{'='*50}")
    print(f"Testing {query_type} Query Builder")
    print(f"{'='*50}")

    for i, test_case in enumerate(test_queries, 1):
        test_name = f"Test {i}: {test_case['description']}"
        print(f"\n{test_name}")
        print(f"Intent: {test_case['intent']}")
        print(f"Entities: {test_case['entities']}")
        print(f"Operators: {test_case['operators']}")
        print(f"Values: {test_case['values']}")
        print(f"Expected Pattern: '{test_case['expected_pattern']}'")
        
        try:
            query, db = build_query(
                test_case['intent'],
                test_case['entities'],
                test_case['operators'],
                test_case['values']
            )
            
            print(f"Generated SQL: '{query}'")
            print(f"Database: '{db}'")
            
            # Check if expected pattern is in the generated query
            if test_case['expected_pattern'] in query:
                print("✅ PASS - Expected pattern found")
                test_results.add_result(query_type, test_case['description'], 'PASS')
            else:
                print("❌ FAIL - Expected pattern NOT found")
                
                # Detailed failure analysis
                failure_analysis = analyze_failure(test_case['expected_pattern'], query)
                
                print(f"🔍 FAILURE ANALYSIS:")
                for key, value in failure_analysis.items():
                    print(f"   {key}: {value}")
                
                # Show side-by-side comparison for short strings
                if len(test_case['expected_pattern']) < 100 and len(query) < 100:
                    print(f"🔍 SIDE-BY-SIDE COMPARISON:")
                    print(f"   Expected: '{test_case['expected_pattern']}'")
                    print(f"   Generated: '{query}'")
                
                test_results.add_result(
                    query_type, 
                    test_case['description'], 
                    'FAIL',
                    f"Expected '{test_case['expected_pattern']}' not found in '{query}'",
                    failure_analysis
                )
                
        except Exception as e:
            print(f"🚫 ERROR - Exception occurred: {e}")
            
            # Enhanced error reporting
            import traceback
            error_details = {
                'Exception Type': type(e).__name__,
                'Exception Message': str(e),
                'Traceback': traceback.format_exc()
            }
            
            print(f"🔍 ERROR DETAILS:")
            print(f"   Exception Type: {type(e).__name__}")
            print(f"   Exception Message: {str(e)}")
            print(f"   Full Traceback:")
            print(f"   {traceback.format_exc()}")
            
            test_results.add_result(
                query_type, 
                test_case['description'], 
                'ERROR', 
                str(e),
                error_details
            )

def main():
    """Run all query builder tests with enhanced debugging"""
    print("Enhanced Query Builder Test Suite")
    print("=" * 60)
    print("This version provides detailed failure analysis to help identify issues")
    print("=" * 60)

    test_results = TestResults()

    for query_type, test_queries in ALL_TEST_QUERIES.items():
        test_query_builder(query_type, test_queries, test_results)

    # Print comprehensive summary
    test_results.print_summary()

if __name__ == "__main__":
    main()
