#!/bin/bash

# End-to-End Testing Script
# Tests all major functionality of the application

set -e  # Exit on error

echo "🧪 End-to-End Testing Script"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Navigate to backend directory
cd backend

echo "1️⃣  Backend Tests"
echo "=================="

# Activate virtual environment
source venv/bin/activate

# Test 1: Check if Django can start
run_test "Django configuration" "python manage.py check --deploy"

# Test 2: Run migrations check
run_test "Database migrations" "python manage.py makemigrations --check --dry-run"

# Test 3: Run authentication tests
run_test "Authentication module" "python manage.py test authentication.tests --verbosity=0"

# Test 4: Run chat tests
run_test "Chat module" "python manage.py test chat.tests --verbosity=0"

# Test 5: Run profiles tests
run_test "Profiles module" "python manage.py test profiles.tests --verbosity=0"

# Test 6: Run matchmaking tests
run_test "Matchmaking module" "python manage.py test matchmaking.tests --verbosity=0"

# Test 7: Run reports tests
run_test "Reports module" "python manage.py test reports.tests --verbosity=0"

# Test 8: Run reputation tests
run_test "Reputation module" "python manage.py test reputation.tests --verbosity=0"

# Test 9: Run security tests
run_test "Security module" "python manage.py test security.tests --verbosity=0"

# Test 10: Run admin dashboard tests
run_test "Admin dashboard" "python manage.py test admin_dashboard.tests --verbosity=0"

echo ""
echo "2️⃣  Frontend Tests"
echo "=================="

cd ../frontend

# Test 11: Check if npm packages are installed
run_test "NPM dependencies" "npm list --depth=0"

# Test 12: TypeScript compilation
run_test "TypeScript compilation" "npx tsc --noEmit"

# Test 13: ESLint check
run_test "ESLint validation" "npm run lint"

# Test 14: Build frontend
run_test "Frontend build" "npm run build"

echo ""
echo "3️⃣  Integration Tests"
echo "====================="

cd ../backend

# Test 15: Check API endpoints
run_test "API health check" "python manage.py check"

# Test 16: Check static files
run_test "Static files collection" "python manage.py collectstatic --noinput --clear"

echo ""
echo "4️⃣  Security Tests"
echo "=================="

# Test 17: Check for security issues
run_test "Security check" "python manage.py check --deploy"

# Test 18: Check for missing migrations
run_test "Migration consistency" "python manage.py makemigrations --check"

echo ""
echo "=============================="
echo "📊 Test Results"
echo "=============================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo "Total: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "🎯 Next steps:"
    echo "   1. Start the development server"
    echo "   2. Test the application manually"
    echo "   3. Review logs for any warnings"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    echo "🔍 Please review the failed tests above"
    echo "   Run individual tests for more details"
    exit 1
fi
