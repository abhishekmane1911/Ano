#!/usr/bin/env python
"""
Test script for spam detection system
Demonstrates smart detection that allows natural chat while blocking spam
"""
import asyncio
import sys
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
import django
django.setup()

from chat.anti_spam import SpamDetectionMiddleware


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


async def test_message(description, messages, should_pass=True):
    """Test a sequence of messages"""
    print(f"\n{Colors.BOLD}{description}{Colors.END}")
    print("-" * 60)
    
    user_id = 1
    chatroom_id = "test_room"
    
    all_passed = True
    for i, content in enumerate(messages, 1):
        allowed, error = await SpamDetectionMiddleware.check_all(
            user_id, chatroom_id, content, 'message.send'
        )
        
        if allowed:
            status = f"{Colors.GREEN}✓ ALLOWED{Colors.END}"
        else:
            status = f"{Colors.RED}✗ BLOCKED{Colors.END}"
            all_passed = False
        
        print(f"  {i}. \"{content}\"")
        print(f"     {status}", end="")
        if error:
            print(f" - {error}")
        else:
            print()
        
        # Small delay between messages
        await asyncio.sleep(0.1)
    
    # Check if result matches expectation
    if should_pass and all_passed:
        print(f"\n{Colors.GREEN}✓ TEST PASSED{Colors.END} - All messages allowed as expected")
    elif not should_pass and not all_passed:
        print(f"\n{Colors.GREEN}✓ TEST PASSED{Colors.END} - Spam blocked as expected")
    elif should_pass and not all_passed:
        print(f"\n{Colors.RED}✗ TEST FAILED{Colors.END} - False positive detected!")
    else:
        print(f"\n{Colors.YELLOW}⚠ TEST WARNING{Colors.END} - Spam not blocked")
    
    return all_passed == should_pass


async def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("SPAM DETECTION SYSTEM - SMART DETECTION TEST")
    print(f"{'='*60}{Colors.END}\n")
    
    results = []
    
    # Test 1: Rapid short responses (should pass)
    results.append(await test_message(
        "Test 1: Rapid Short Responses (Natural Chat)",
        ["ok", "yes", "lol", "haha", "nice", "cool", "omg"],
        should_pass=True
    ))
    
    # Test 2: Natural repetition (should pass)
    results.append(await test_message(
        "Test 2: Natural Repetition (Excitement)",
        ["hahahaha", "yesss", "noooo", "omg omg omg"],
        should_pass=True
    ))
    
    # Test 3: Similar questions (should pass)
    results.append(await test_message(
        "Test 3: Similar Questions (Natural Conversation)",
        [
            "What time is the meeting?",
            "What time is the class?",
            "What time is the event?"
        ],
        should_pass=True
    ))
    
    # Test 4: Excited messages with caps (should pass)
    results.append(await test_message(
        "Test 4: Excited Messages (Short with Caps)",
        ["YESSS!", "OMG!", "WOW!!!", "NICE!"],
        should_pass=True
    ))
    
    # Test 5: Quick reactions (should pass)
    results.append(await test_message(
        "Test 5: Quick Reactions (Natural Chat)",
        ["😂😂😂", "🔥🔥🔥", "❤️❤️", "👍👍"],
        should_pass=True
    ))
    
    # Test 6: Back-and-forth conversation (should pass)
    results.append(await test_message(
        "Test 6: Back-and-Forth Conversation",
        [
            "hey",
            "how are you?",
            "what's up?",
            "did you see the game?",
            "it was crazy",
            "omg",
            "lol"
        ],
        should_pass=True
    ))
    
    # Wait a bit before spam tests
    await asyncio.sleep(2)
    
    # Test 7: Excessive duplicates (should block)
    results.append(await test_message(
        "Test 7: Excessive Duplicates (Spam)",
        [
            "Check out this link!",
            "Check out this link!",
            "Check out this link!",
            "Check out this link!"
        ],
        should_pass=False
    ))
    
    # Test 8: Very similar spam (should block)
    results.append(await test_message(
        "Test 8: Very Similar Messages (Spam)",
        [
            "Buy this product now for discount",
            "Buy this product now for discounts",
            "Buy this product now for big discount"
        ],
        should_pass=False
    ))
    
    # Test 9: Excessive repetition (should block)
    results.append(await test_message(
        "Test 9: Excessive Repetition (Spam)",
        ["aaaaaaaaaaaaaaaa"],
        should_pass=False
    ))
    
    # Test 10: Commercial spam (should block)
    results.append(await test_message(
        "Test 10: Commercial Spam Keywords",
        ["CLICK HERE NOW!!! BUY NOW LIMITED OFFER!!!"],
        should_pass=False
    ))
    
    # Test 11: URL spam (should block)
    results.append(await test_message(
        "Test 11: URL Spam",
        ["Check http://spam.com and www.spam.net and spam.org now!"],
        should_pass=False
    ))
    
    # Test 12: Emoji spam (should block)
    results.append(await test_message(
        "Test 12: Emoji Spam",
        ["😀😀😀😀😀😀😀😀😀😀😀😀😀😀😀😀😀😀😀😀"],
        should_pass=False
    ))
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Colors.END}\n")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {Colors.GREEN}{passed}/{total}{Colors.END}")
    print(f"Tests Failed: {Colors.RED}{total - passed}/{total}{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}The spam detection system is working perfectly!{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
        print(f"{Colors.RED}Please review the failed tests above{Colors.END}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return passed == total


if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
