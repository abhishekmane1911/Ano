from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from unittest.mock import Mock, patch
from .models import UserReputation, MessageRanking, Vote
from .services import ReputationService, VotingService, TierPrivilegeManager, WilsonScoreCalculator, require_privilege, require_privilege_drf
from .middleware import TierPrivilegeMiddleware
from chat.models import Message, Chatroom
from profiles.models import Profile

User = get_user_model()


class UserReputationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
        # Get the automatically created reputation
        self.reputation = UserReputation.objects.get(user=self.user)
    
    def test_user_reputation_creation(self):
        """Test that UserReputation is created with correct defaults"""
        self.assertEqual(self.reputation.reputation_score, 0.0)
        self.assertEqual(self.reputation.rank_tier, 'Fresher')
        self.assertEqual(self.reputation.total_upvotes_received, 0)
        self.assertEqual(self.reputation.total_downvotes_received, 0)
    
    def test_calculate_level(self):
        """Test level calculation using logarithmic progression"""
        # Test level 0 for score < 100
        self.assertEqual(self.reputation.calculate_level(), 0)
        
        # Test level 1 for score = 100
        self.reputation.reputation_score = 100
        self.assertEqual(self.reputation.calculate_level(), 1)
        
        # Test level 2 for score = 150 (100 * 1.5^1)
        self.reputation.reputation_score = 150
        self.assertEqual(self.reputation.calculate_level(), 2)
        
        # Test level 3 for score = 225 (100 * 1.5^2)
        self.reputation.reputation_score = 225
        self.assertEqual(self.reputation.calculate_level(), 3)
    
    def test_update_tier(self):
        """Test tier updates based on reputation score"""
        # Test Sophomore tier
        self.reputation.reputation_score = 100
        tier = self.reputation.update_tier()
        self.assertEqual(tier, 'Sophomore')
        
        # Test Senior tier
        self.reputation.reputation_score = 500
        tier = self.reputation.update_tier()
        self.assertEqual(tier, 'Senior')
        
        # Test Campus Legend tier
        self.reputation.reputation_score = 1000
        tier = self.reputation.update_tier()
        self.assertEqual(tier, 'Campus Legend')


class TierPrivilegeManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
        self.reputation = UserReputation.objects.get(user=self.user)
    
    def test_has_privilege_fresher(self):
        """Test Fresher tier privileges"""
        self.assertTrue(TierPrivilegeManager.has_privilege('Fresher', 'read'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Fresher', 'write'))
        self.assertFalse(TierPrivilegeManager.has_privilege('Fresher', 'vote'))
        self.assertFalse(TierPrivilegeManager.has_privilege('Fresher', 'upload_images'))
    
    def test_has_privilege_sophomore(self):
        """Test Sophomore tier privileges"""
        self.assertTrue(TierPrivilegeManager.has_privilege('Sophomore', 'read'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Sophomore', 'write'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Sophomore', 'vote'))
        self.assertFalse(TierPrivilegeManager.has_privilege('Sophomore', 'upload_images'))
    
    def test_has_privilege_senior(self):
        """Test Senior tier privileges"""
        self.assertTrue(TierPrivilegeManager.has_privilege('Senior', 'read'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Senior', 'write'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Senior', 'vote'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Senior', 'upload_images'))
        self.assertFalse(TierPrivilegeManager.has_privilege('Senior', 'create_polls'))
    
    def test_has_privilege_campus_legend(self):
        """Test Campus Legend tier privileges"""
        self.assertTrue(TierPrivilegeManager.has_privilege('Campus Legend', 'read'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Campus Legend', 'write'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Campus Legend', 'vote'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Campus Legend', 'upload_images'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Campus Legend', 'create_polls'))
        self.assertTrue(TierPrivilegeManager.has_privilege('Campus Legend', 'create_confessions'))
    
    def test_get_required_tier(self):
        """Test getting required tier for actions"""
        self.assertEqual(TierPrivilegeManager.get_required_tier('read'), 'Fresher')
        self.assertEqual(TierPrivilegeManager.get_required_tier('write'), 'Fresher')
        self.assertEqual(TierPrivilegeManager.get_required_tier('vote'), 'Sophomore')
        self.assertEqual(TierPrivilegeManager.get_required_tier('upload_images'), 'Senior')
        self.assertEqual(TierPrivilegeManager.get_required_tier('create_polls'), 'Campus Legend')
    
    def test_check_user_privilege(self):
        """Test checking user privileges based on current tier"""
        # Fresher user
        self.assertTrue(TierPrivilegeManager.check_user_privilege(self.user, 'read'))
        self.assertTrue(TierPrivilegeManager.check_user_privilege(self.user, 'write'))
        self.assertFalse(TierPrivilegeManager.check_user_privilege(self.user, 'vote'))
        
        # Upgrade to Sophomore
        self.reputation.reputation_score = 100
        self.reputation.update_tier()
        
        self.assertTrue(TierPrivilegeManager.check_user_privilege(self.user, 'vote'))
        self.assertFalse(TierPrivilegeManager.check_user_privilege(self.user, 'upload_images'))
    
    def test_get_privilege_info(self):
        """Test getting detailed privilege information"""
        info = TierPrivilegeManager.get_privilege_info(self.user, 'vote')
        
        self.assertFalse(info['has_privilege'])
        self.assertEqual(info['current_tier'], 'Fresher')
        self.assertEqual(info['required_tier'], 'Sophomore')
        self.assertEqual(info['current_score'], 0.0)
        self.assertEqual(info['action'], 'vote')
        self.assertIn('read', info['all_privileges'])
        self.assertIn('write', info['all_privileges'])


class PrivilegeDecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
        self.reputation = UserReputation.objects.get(user=self.user)
    
    def test_require_privilege_decorator_success(self):
        """Test privilege decorator allows access when user has privilege"""
        @require_privilege('read', return_json=True)
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.user = self.user
        
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_require_privilege_decorator_failure(self):
        """Test privilege decorator blocks access when user lacks privilege"""
        @require_privilege('vote', return_json=True)
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.user = self.user
        
        response = test_view(request)
        self.assertEqual(response.status_code, 403)
        
        # Check error response content
        import json
        data = json.loads(response.content)
        self.assertEqual(data['code'], 'INSUFFICIENT_PRIVILEGES')
        self.assertIn('vote requires Sophomore', data['error'])
    
    def test_require_privilege_decorator_unauthenticated(self):
        """Test privilege decorator handles unauthenticated users"""
        @require_privilege('read', return_json=True)
        def test_view(request):
            return JsonResponse({'success': True})
        
        request = self.factory.get('/test/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = test_view(request)
        self.assertEqual(response.status_code, 401)


class TierPrivilegeMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TierPrivilegeMiddleware(Mock())
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
        self.reputation = UserReputation.objects.get(user=self.user)
    
    def test_middleware_adds_tier_info(self):
        """Test middleware adds tier information to request"""
        request = self.factory.get('/test/')
        request.user = self.user
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Should not block request
        
        # Check that tier info was added
        self.assertEqual(request.user_tier, 'Fresher')
        self.assertEqual(request.user_reputation_score, 0.0)
        self.assertIn('read', request.user_privileges)
        self.assertIn('write', request.user_privileges)
    
    def test_middleware_blocks_insufficient_privilege(self):
        """Test middleware blocks access to privilege-required endpoints"""
        request = self.factory.post('/api/reputation/vote/')
        request.user = self.user
        
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 403)
        
        # Check error response
        import json
        data = json.loads(response.content)
        self.assertEqual(data['code'], 'INSUFFICIENT_PRIVILEGES')
    
    def test_middleware_allows_sufficient_privilege(self):
        """Test middleware allows access when user has sufficient privilege"""
        # Upgrade user to Sophomore
        self.reputation.reputation_score = 100
        self.reputation.update_tier()
        
        request = self.factory.post('/api/reputation/vote/')
        request.user = self.user
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Should not block request


class ReputationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
    
    def test_get_or_create_reputation(self):
        """Test reputation creation service"""
        reputation = ReputationService.get_or_create_reputation(self.user)
        
        self.assertIsInstance(reputation, UserReputation)
        self.assertEqual(reputation.user, self.user)
        self.assertEqual(reputation.reputation_score, 0.0)
    
    def test_award_points(self):
        """Test point awarding system"""
        initial_score = 0.0
        
        # Award upvote points
        result = ReputationService.award_points(self.user, 'message_upvote')
        self.assertEqual(result['new_score'], initial_score + 5)
        self.assertEqual(result['points_awarded'], 5)
        self.assertEqual(result['action'], 'message_upvote')
        
        # Award downvote points (negative)
        result = ReputationService.award_points(self.user, 'message_downvote')
        self.assertEqual(result['new_score'], initial_score + 5 - 2)
        self.assertEqual(result['points_awarded'], -2)
    
    def test_check_tier_privileges(self):
        """Test tier privilege checking"""
        reputation = ReputationService.get_or_create_reputation(self.user)
        
        # Fresher can read and write
        self.assertTrue(ReputationService.check_tier_privileges(self.user, 'read'))
        self.assertTrue(ReputationService.check_tier_privileges(self.user, 'write'))
        self.assertFalse(ReputationService.check_tier_privileges(self.user, 'vote'))
        
        # Upgrade to Sophomore
        reputation.reputation_score = 100
        reputation.update_tier()
        
        # Sophomore can vote
        self.assertTrue(ReputationService.check_tier_privileges(self.user, 'vote'))
        self.assertFalse(ReputationService.check_tier_privileges(self.user, 'upload_images'))


class WilsonScoreCalculatorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            age=20,
            interests=['coding', 'music'],
            relationship_intent='friendship',
            bio='Test bio'
        )
        self.chatroom = Chatroom.objects.create(
            name='Test Room',
            description='Test room'
        )
        self.message = Message.objects.create(
            sender=self.profile,
            chatroom=self.chatroom,
            content='Test message'
        )
    
    def test_wilson_score_calculation_no_votes(self):
        """Test Wilson Score calculation with no votes"""
        score = WilsonScoreCalculator.calculate_score(0, 0)
        self.assertEqual(score, 0.0)
    
    def test_wilson_score_calculation_all_upvotes(self):
        """Test Wilson Score calculation with all upvotes"""
        score = WilsonScoreCalculator.calculate_score(10, 10)
        self.assertGreater(score, 0.7)  # Should be high with all upvotes
        self.assertLess(score, 1.0)     # But less than 1.0 due to confidence interval
    
    def test_wilson_score_calculation_mixed_votes(self):
        """Test Wilson Score calculation with mixed votes"""
        # 7 upvotes out of 10 total votes
        score = WilsonScoreCalculator.calculate_score(7, 10)
        self.assertGreater(score, 0.35)  # Should be positive
        self.assertLess(score, 0.8)      # But not as high as all upvotes
    
    def test_wilson_score_calculation_controversial(self):
        """Test Wilson Score calculation with controversial content (50/50 split)"""
        # 50 upvotes out of 100 total votes
        score = WilsonScoreCalculator.calculate_score(50, 100)
        self.assertGreater(score, 0.3)  # Should be around 0.4 for 50/50 split
        self.assertLess(score, 0.6)
    
    def test_wilson_score_vs_simple_ratio(self):
        """Test that Wilson Score differs from simple upvote ratio"""
        # Small sample: 1 upvote out of 1 vote
        wilson_small = WilsonScoreCalculator.calculate_score(1, 1)
        simple_ratio_small = 1.0
        
        # Large sample: 100 upvotes out of 100 votes
        wilson_large = WilsonScoreCalculator.calculate_score(100, 100)
        simple_ratio_large = 1.0
        
        # Wilson Score should be more conservative with small samples
        self.assertLess(wilson_small, simple_ratio_small)
        self.assertGreater(wilson_large, wilson_small)  # More confidence with larger sample
    
    def test_update_message_ranking(self):
        """Test updating message ranking with Wilson Score"""
        # Create some votes first
        ranking, created = MessageRanking.objects.get_or_create(message=self.message)
        ranking.upvotes = 8
        ranking.downvotes = 2
        ranking.save()
        
        # Update Wilson Score
        score = WilsonScoreCalculator.update_message_ranking(self.message)
        
        # Verify the score was calculated and saved
        ranking.refresh_from_db()
        self.assertEqual(ranking.wilson_score, score)
        self.assertGreater(score, 0.45)  # Should be positive with more upvotes


class MessageRankingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            age=20,
            interests=['coding', 'music'],
            relationship_intent='friendship',
            bio='Test bio'
        )
        self.chatroom = Chatroom.objects.create(
            name='Test Room',
            description='Test room'
        )
        self.message = Message.objects.create(
            sender=self.profile,
            chatroom=self.chatroom,
            content='Test message'
        )
        self.ranking = MessageRanking.objects.create(
            message=self.message,
            upvotes=5,
            downvotes=2
        )
    
    def test_calculate_wilson_score_method(self):
        """Test the calculate_wilson_score method on the model"""
        score = self.ranking.calculate_wilson_score()
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)
        
        # Test with different vote counts
        self.ranking.upvotes = 10
        self.ranking.downvotes = 1
        high_score = self.ranking.calculate_wilson_score()
        
        self.ranking.upvotes = 1
        self.ranking.downvotes = 10
        low_score = self.ranking.calculate_wilson_score()
        
        self.assertGreater(high_score, low_score)
    
    def test_update_wilson_score_method(self):
        """Test the update_wilson_score method saves the calculated score"""
        old_score = self.ranking.wilson_score
        self.ranking.update_wilson_score()
        
        self.ranking.refresh_from_db()
        self.assertNotEqual(self.ranking.wilson_score, old_score)
        self.assertGreater(self.ranking.wilson_score, 0.0)


class VotingServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
        self.author = User.objects.create_user(
            username='author',
            email='author@iiti.ac.in',
            password='testpass123'
        )
        self.user_profile = Profile.objects.create(
            user=self.user,
            age=20,
            interests=['coding'],
            relationship_intent='friendship',
            bio='Test bio'
        )
        self.author_profile = Profile.objects.create(
            user=self.author,
            age=21,
            interests=['writing'],
            relationship_intent='friendship',
            bio='Author bio'
        )
        self.chatroom = Chatroom.objects.create(
            name='Test Room',
            description='Test room'
        )
        self.message = Message.objects.create(
            sender=self.author_profile,
            chatroom=self.chatroom,
            content='Test message'
        )
        
        # Upgrade user to Sophomore so they can vote
        reputation = UserReputation.objects.get(user=self.user)
        reputation.reputation_score = 100
        reputation.update_tier()
    
    def test_cast_vote_success(self):
        """Test successful vote casting"""
        result = VotingService.cast_vote(self.user, self.message, 'upvote')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['vote_type'], 'upvote')
        self.assertIn('reputation_update', result)
        
        # Verify vote was created
        vote = Vote.objects.get(user=self.user, message=self.message)
        self.assertEqual(vote.vote_type, 'upvote')
        
        # Verify message ranking was updated
        ranking = MessageRanking.objects.get(message=self.message)
        self.assertEqual(ranking.upvotes, 1)
        self.assertEqual(ranking.downvotes, 0)
        self.assertGreater(ranking.wilson_score, 0.0)
    
    def test_cast_vote_insufficient_privilege(self):
        """Test vote casting with insufficient privileges"""
        # Create a Fresher user (can't vote)
        fresher = User.objects.create_user(
            username='fresher',
            email='fresher@iiti.ac.in',
            password='testpass123'
        )
        
        result = VotingService.cast_vote(fresher, self.message, 'upvote')
        
        self.assertFalse(result['success'])
        self.assertIn('Insufficient privileges', result['error'])
        self.assertIn('privilege_info', result)
    
    def test_cast_vote_change_vote(self):
        """Test changing an existing vote"""
        # Cast initial upvote
        VotingService.cast_vote(self.user, self.message, 'upvote')
        
        # Change to downvote
        result = VotingService.cast_vote(self.user, self.message, 'downvote')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['vote_type'], 'downvote')
        
        # Verify vote was updated
        vote = Vote.objects.get(user=self.user, message=self.message)
        self.assertEqual(vote.vote_type, 'downvote')
        
        # Verify only one vote exists
        vote_count = Vote.objects.filter(user=self.user, message=self.message).count()
        self.assertEqual(vote_count, 1)
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
    
    def test_get_or_create_reputation(self):
        """Test reputation creation service"""
        reputation = ReputationService.get_or_create_reputation(self.user)
        
        self.assertIsInstance(reputation, UserReputation)
        self.assertEqual(reputation.user, self.user)
        self.assertEqual(reputation.reputation_score, 0.0)
    
    def test_award_points(self):
        """Test point awarding system"""
        initial_score = 0.0
        
        # Award upvote points
        result = ReputationService.award_points(self.user, 'message_upvote')
        self.assertEqual(result['new_score'], initial_score + 5)
        self.assertEqual(result['points_awarded'], 5)
        self.assertEqual(result['action'], 'message_upvote')
        
        # Award downvote points (negative)
        result = ReputationService.award_points(self.user, 'message_downvote')
        self.assertEqual(result['new_score'], initial_score + 5 - 2)
        self.assertEqual(result['points_awarded'], -2)
    
    def test_check_tier_privileges(self):
        """Test tier privilege checking"""
        reputation = ReputationService.get_or_create_reputation(self.user)
        
        # Fresher can read and write
        self.assertTrue(ReputationService.check_tier_privileges(self.user, 'read'))
        self.assertTrue(ReputationService.check_tier_privileges(self.user, 'write'))
        self.assertFalse(ReputationService.check_tier_privileges(self.user, 'vote'))
        
        # Upgrade to Sophomore
        reputation.reputation_score = 100
        reputation.update_tier()
        
        # Sophomore can vote
        self.assertTrue(ReputationService.check_tier_privileges(self.user, 'vote'))
        self.assertFalse(ReputationService.check_tier_privileges(self.user, 'upload_images'))
