# Implementation Plan

- [x] 1. Set up project structure and development environment
  - Create frontend React + TypeScript project with Vite
  - Create backend Django project with modular app structure
  - Set up PostgreSQL and Redis with Docker Compose
  - Configure environment variables for both frontend and backend
  - Set up Git repository with .gitignore files
  - Install and configure linting tools (ESLint, Flake8, Prettier, Black)
  - _Requirements: All_

- [x] 2. Implement authentication backend
  - Create Django auth app with custom User model extending AbstractUser
  - Implement email domain validation for @iiti.ac.in
  - Set up Argon2 password hashing
  - Configure djangorestframework-simplejwt for JWT tokens
  - Create registration endpoint with email verification token generation
  - Create email verification endpoint to activate accounts
  - Create login endpoint returning access and refresh tokens
  - Create token refresh endpoint
  - Create logout endpoint to invalidate refresh tokens
  - Implement rate limiting middleware for login attempts
  - _Requirements: 1.1, 1.2, 1.3, 1.5, 2.1, 2.3, 2.4, 2.5_

- [ ]* 2.1 Write property test for email domain validation
  - **Property 1: Email domain validation**
  - **Validates: Requirements 1.1**

- [ ]* 2.2 Write property test for password hashing
  - **Property 4: Password hashing**
  - **Validates: Requirements 1.5**

- [ ]* 2.3 Write property test for JWT token generation
  - **Property 5: JWT token generation**
  - **Validates: Requirements 2.1**

- [ ]* 2.4 Write property test for token refresh round-trip
  - **Property 8: Token refresh round-trip**
  - **Validates: Requirements 2.4**

- [ ]* 2.5 Write property test for rate limiting
  - **Property 9: Rate limiting on failed logins**
  - **Validates: Requirements 2.5**

- [x] 3. Implement authentication frontend
  - Create Zustand store for authentication state
  - Create LandingPage component with hero section
  - Create SignupForm component with email validation
  - Create LoginForm component with remember me option
  - Create EmailVerification component
  - Create PasswordReset flow components
  - Implement Axios interceptors for JWT token handling
  - Set up automatic token refresh on 401 responses
  - Store refresh token in HTTP-only cookie
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4_

- [ ]* 3.1 Write property test for secure cookie storage
  - **Property 6: Secure cookie storage**
  - **Validates: Requirements 2.2**

- [ ]* 3.2 Write property test for token validation
  - **Property 7: Token validation**
  - **Validates: Requirements 2.3**

- [x] 4. Implement profile system backend
  - Create profiles Django app with Profile model
  - Add UUID field for anonymous_id
  - Add fields for interests, hobbies, age, relationship_intent, personality_tags
  - Create profile creation endpoint
  - Create profile retrieval endpoint (by anonymous_id only)
  - Create profile update endpoint with server-side validation
  - Implement avatar upload with anonymity filters
  - Ensure no API response includes user email or real name
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 14.1, 14.2, 14.4_

- [ ]* 4.1 Write property test for UUID assignment
  - **Property 13: UUID assignment**
  - **Validates: Requirements 3.1**

- [ ]* 4.2 Write property test for personal information isolation
  - **Property 14: Personal information isolation**
  - **Validates: Requirements 3.2, 3.4, 14.4**

- [ ]* 4.3 Write property test for server-side profile validation
  - **Property 15: Server-side profile validation**
  - **Validates: Requirements 3.5**

- [ ]* 4.4 Write property test for UUID format consistency
  - **Property 17: UUID format consistency**
  - **Validates: Requirements 14.1**

- [ ]* 4.5 Write property test for anonymous relationship storage
  - **Property 18: Anonymous relationship storage**
  - **Validates: Requirements 14.2**

- [x] 5. Implement profile system frontend
  - Create ProfileCreation multi-step form component
  - Create ProfileEditor component
  - Create AnonymousAvatar component with filter preview
  - Create InterestSelector tag-based component
  - Implement profile image upload with preview
  - Add client-side validation for profile fields
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [x] 6. Implement chatroom backend
  - Create chat Django app with Chatroom and Message models
  - Add MessageReaction and ReadReceipt models
  - Create chatroom list endpoint
  - Create chatroom detail endpoint
  - Create message list endpoint with pagination
  - Create message send endpoint
  - Create message edit endpoint
  - Create message delete endpoint
  - Create message reaction endpoint
  - Create message pin/unpin endpoint
  - Implement media upload with compression
  - Add indexes for efficient message queries
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.2, 5.4, 5.5_

- [ ]* 6.1 Write property test for anonymous chatroom display
  - **Property 16: Anonymous chatroom display**
  - **Validates: Requirements 4.1**

- [ ]* 6.2 Write property test for media compression
  - **Property 21: Media compression**
  - **Validates: Requirements 4.3**

- [ ]* 6.3 Write property test for message pinning
  - **Property 23: Message pinning**
  - **Validates: Requirements 4.5**

- [ ]* 6.4 Write property test for read receipt creation
  - **Property 25: Read receipt creation**
  - **Validates: Requirements 5.2, 8.5**

- [ ]* 6.5 Write property test for reaction storage
  - **Property 27: Reaction storage and broadcasting**
  - **Validates: Requirements 5.4**

- [ ]* 6.6 Write property test for paginated message loading
  - **Property 28: Paginated message loading**
  - **Validates: Requirements 5.5**

- [x] 7. Implement WebSocket backend for chat
  - Install and configure Django Channels
  - Set up Redis channel layer
  - Create ChatConsumer for chatroom WebSocket connections
  - Implement JWT authentication for WebSocket connections
  - Handle message.send, message.receive events
  - Handle message.edit, message.delete events
  - Handle message.react event
  - Handle typing.start, typing.stop events
  - Handle user.join, user.leave events
  - Handle read.receipt event
  - Implement WebSocket rate limiting
  - _Requirements: 4.2, 4.4, 5.1, 5.2, 5.3, 5.4_

- [ ]* 7.1 Write property test for real-time message broadcasting
  - **Property 20: Real-time message broadcasting**
  - **Validates: Requirements 4.2**

- [ ]* 7.2 Write property test for message mutation broadcasting
  - **Property 22: Message mutation broadcasting**
  - **Validates: Requirements 4.4**

- [ ]* 7.3 Write property test for typing indicator broadcasting
  - **Property 24: Typing indicator broadcasting**
  - **Validates: Requirements 5.1**

- [ ]* 7.4 Write property test for anonymous presence updates
  - **Property 26: Anonymous presence updates**
  - **Validates: Requirements 5.3**

- [x] 8. Implement chatroom frontend
  - Create ChatroomList component with unread counts
  - Create ChatWindow component with infinite scroll
  - Create MessageInput component with emoji picker
  - Create MessageBubble component with reactions
  - Create TypingIndicator animated component
  - Create MediaViewer full-screen component
  - Create MessageReactions component
  - Create PinnedMessages collapsible section
  - Set up Socket.IO client connection
  - Implement WebSocket event handlers for all chat events
  - Add optimistic UI updates for sent messages
  - Implement automatic reconnection on disconnect
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 9. Implement matchmaking backend
  - Create matchmaking Django app with Swipe and Match models
  - Create profiles endpoint for swiping (exclude already swiped)
  - Create swipe endpoint to record left/right swipes
  - Implement mutual match detection logic
  - Create matches list endpoint
  - Create match detail endpoint
  - Create match messages endpoint with pagination
  - Create match message send endpoint
  - Ensure blocked users don't appear in profiles
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 9.4_

- [ ]* 9.1 Write property test for profile card completeness
  - **Property 33: Profile card completeness**
  - **Validates: Requirements 7.1**

- [ ]* 9.2 Write property test for swipe left recording
  - **Property 34: Swipe left recording**
  - **Validates: Requirements 7.2**

- [ ]* 9.3 Write property test for swipe right recording
  - **Property 35: Swipe right recording**
  - **Validates: Requirements 7.3**

- [ ]* 9.4 Write property test for mutual match creation
  - **Property 36: Mutual match creation**
  - **Validates: Requirements 7.4**

- [ ]* 9.5 Write property test for profile exclusion after swipe
  - **Property 37: Profile exclusion after swipe**
  - **Validates: Requirements 7.5**

- [ ]* 9.6 Write property test for match chat initialization
  - **Property 38: Match chat initialization**
  - **Validates: Requirements 8.1**

- [x] 10. Implement WebSocket backend for match chat
  - Create MatchConsumer for match chat WebSocket connections
  - Verify both users are part of the match before allowing connection
  - Handle message.send, message.receive events for matches
  - Handle typing.start, typing.stop events for matches
  - Handle read.receipt event for matches
  - _Requirements: 8.2, 8.4, 8.5_

- [ ]* 10.1 Write property test for match chat message delivery
  - **Property 31: Match chat message delivery**
  - **Validates: Requirements 8.2**

- [ ]* 10.2 Write property test for match chat typing indicator
  - **Property 32: Match chat typing indicator**
  - **Validates: Requirements 8.4**

- [x] 11. Implement matchmaking frontend
  - Create SwipeCard component with profile display
  - Create SwipeInterface with Tinder-style card stack
  - Implement swipe gesture handlers (left/right)
  - Create MatchNotification modal with celebration animation
  - Create MatchList component
  - Create MatchChat component reusing chat UI
  - Add Framer Motion animations for card swipes
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 12. Implement reports and blocking backend
  - Create reports Django app with Report and Block models
  - Create report submission endpoint with anonymous IDs
  - Create block user endpoint
  - Create blocked users list endpoint
  - Create unblock user endpoint
  - Implement report escalation logic for multiple reports
  - Send admin notifications for escalated reports
  - Filter blocked users from matchmaking and chat
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ]* 12.1 Write property test for anonymous report creation
  - **Property 39: Anonymous report creation**
  - **Validates: Requirements 9.1**

- [ ]* 12.2 Write property test for block communication prevention
  - **Property 40: Block communication prevention**
  - **Validates: Requirements 9.2**

- [ ]* 12.3 Write property test for anonymous admin notifications
  - **Property 41: Anonymous admin notifications**
  - **Validates: Requirements 9.3**

- [ ]* 12.4 Write property test for blocked profile filtering
  - **Property 42: Blocked profile filtering**
  - **Validates: Requirements 9.4**

- [ ]* 12.5 Write property test for report escalation
  - **Property 30: Report escalation**
  - **Validates: Requirements 6.3, 9.5**

- [x] 13. Implement reports and blocking frontend
  - Create ReportModal component with reason selection
  - Create BlockConfirmation dialog component
  - Create SafetySettings component
  - Add report and block buttons to chat and profile views
  - Implement report submission flow
  - Implement block confirmation flow
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 14. Implement admin dashboard backend
  - Create admin_dashboard Django app
  - Create reports list endpoint for admins
  - Create report update endpoint (status changes)
  - Create user detail endpoint for moderation (anonymous IDs only)
  - Create user ban endpoint
  - Create broadcast message endpoint
  - Create platform metrics endpoint (active users, message volume)
  - Ensure all admin views use anonymous identifiers
  - _Requirements: 6.1, 6.2, 6.3, 15.1, 15.2, 15.3, 15.4_

- [ ]* 14.1 Write property test for admin broadcast designation
  - **Property 29: Admin broadcast designation**
  - **Validates: Requirements 6.1**

- [ ]* 14.2 Write property test for anonymous admin dashboard
  - **Property 47: Anonymous admin dashboard**
  - **Validates: Requirements 15.1, 15.2**

- [ ]* 14.3 Write property test for report action recording
  - **Property 48: Report action recording**
  - **Validates: Requirements 15.3**

- [ ]* 14.4 Write property test for platform metrics calculation
  - **Property 49: Platform metrics calculation**
  - **Validates: Requirements 15.4**

- [x] 15. Implement admin dashboard frontend
  - Create AdminDashboard page component
  - Create ReportsList component with filtering
  - Create ReportDetail component
  - Create UserModerationPanel component
  - Create BroadcastMessageForm component
  - Create PlatformMetrics component with charts
  - Add admin-only route protection
  - _Requirements: 6.1, 15.1, 15.2, 15.3, 15.4_

- [x] 16. Implement search functionality
  - Add full-text search to Message model using PostgreSQL
  - Create message search endpoint with query parameter
  - Implement search scope filtering (only accessible chats)
  - Add search result highlighting in response
  - Create SearchBar component in frontend
  - Create SearchResults component with highlighting
  - Implement search result navigation to message
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ]* 16.1 Write property test for search scope limitation
  - **Property 43: Search scope limitation**
  - **Validates: Requirements 10.1, 10.4**

- [ ]* 16.2 Write property test for search result highlighting
  - **Property 44: Search result highlighting**
  - **Validates: Requirements 10.2**

- [x] 17. Implement theme system
  - Create theme context in React
  - Create ThemeToggle component
  - Define light and dark color schemes in Tailwind config
  - Implement theme persistence in local storage
  - Apply theme classes to root element
  - Ensure all components support both themes
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ]* 17.1 Write property test for theme persistence round-trip
  - **Property 45: Theme persistence round-trip**
  - **Validates: Requirements 11.2, 11.3**

- [x] 18. Implement security middleware and protections
  - Configure CORS with allowed origins
  - Implement CSRF protection for all state-changing endpoints
  - Add input validation decorators for all API endpoints
  - Configure Content Security Policy headers
  - Implement file upload validation (type, size, malware scanning)
  - Add HTTPS redirect middleware
  - Configure secure cookie settings
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 18.1 Write property test for CSRF protection
  - **Property 10: CSRF protection**
  - **Validates: Requirements 12.2**

- [ ]* 18.2 Write property test for input validation
  - **Property 11: Input validation**
  - **Validates: Requirements 12.1**

- [ ]* 18.3 Write property test for file type validation
  - **Property 12: File type validation**
  - **Validates: Requirements 12.5**

- [x] 19. Implement responsive design and mobile optimization
  - Configure Tailwind breakpoints for mobile, tablet, desktop
  - Make all components responsive with mobile-first approach
  - Implement touch gesture handlers for swipe interface
  - Add viewport meta tags for mobile
  - Implement mobile media optimization endpoint
  - Create mobile-optimized navigation
  - Test on various screen sizes
  - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [ ]* 19.1 Write property test for mobile media optimization
  - **Property 46: Mobile media optimization**
  - **Validates: Requirements 13.4**

- [x] 20. Implement logging with anonymity
  - Configure Django logging with custom formatter
  - Create logging middleware that uses anonymous IDs
  - Add logging to all critical operations
  - Ensure no logs contain emails or real names
  - Set up log rotation and retention
  - _Requirements: 14.3_

- [ ]* 20.1 Write property test for anonymous logging
  - **Property 19: Anonymous logging**
  - **Validates: Requirements 14.3**

- [x] 21. Add animations and polish
  - Add Framer Motion animations to page transitions
  - Add smooth animations to card swipes
  - Add loading skeletons for async content
  - Add toast notifications for user actions
  - Add smooth scroll behavior
  - Add hover effects and micro-interactions
  - Ensure animations respect prefers-reduced-motion
  - _Requirements: 11.1_

- [x] 22. Implement email service
  - Configure Django email backend (SMTP)
  - Create email templates for verification
  - Create email templates for password reset
  - Set up Celery for async email sending
  - Add email sending to registration flow
  - Add email sending to password reset flow
  - _Requirements: 1.2_

- [ ]* 22.1 Write property test for verification email delivery
  - **Property 2: Verification email delivery**
  - **Validates: Requirements 1.2**

- [ ]* 22.2 Write property test for account activation
  - **Property 3: Account activation via verification**
  - **Validates: Requirements 1.3**

- [x] 23. Set up production deployment configuration
  - Create Dockerfile for frontend (multi-stage build)
  - Create Dockerfile for backend
  - Create docker-compose.yml for all services
  - Configure Nginx as reverse proxy
  - Set up Gunicorn for WSGI
  - Set up Daphne for ASGI (WebSockets)
  - Create production environment variable templates
  - Configure PostgreSQL with connection pooling
  - Configure Redis for production
  - Add health check endpoints
  - _Requirements: All_

- [x] 24. Create documentation
  - Write comprehensive README with setup instructions
  - Document all API endpoints with OpenAPI/Swagger
  - Create environment variable template files
  - Write deployment guide
  - Document WebSocket events and payloadsf
  - Create developer onboarding guide
  - _Requirements: All_

- [x] 25. Final checkpoint - Ensure all tests pass
  - Run all unit tests and verify they pass
  - Run all property-based tests and verify they pass
  - Run integration tests for critical flows
  - Fix any failing tests
  - Verify test coverage meets goals
  - Ask the user if questions arise
