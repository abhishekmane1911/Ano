# Requirements Document

## Introduction

Ano is an anonymous chatting and matchmaking platform exclusively for IIT Indore students. The system enables students to communicate anonymously in public chatrooms and engage in Tinder-style matchmaking while maintaining complete anonymity. All users must authenticate using their IIT Indore institute email (@iiti.ac.in) to ensure the platform remains exclusive to the institute community.

## Glossary

- **Ano System**: The complete web application including frontend, backend, and database components
- **Institute Email**: Email address with @iiti.ac.in domain belonging to IIT Indore students
- **Anonymous Profile**: User profile that displays interests and preferences without revealing real identity
- **Chatroom**: Public group chat where multiple users communicate anonymously
- **Match**: Mutual interest between two users indicated by both swiping right
- **Swipe Interface**: Card-based UI where users swipe left (reject) or right (accept) on profiles
- **JWT Token**: JSON Web Token used for secure authentication
- **WebSocket**: Real-time bidirectional communication protocol for instant messaging
- **Anonymous Identifier**: UUID-based identifier that represents a user without revealing personal information
- **Verification Link**: Email-based link sent to institute email for account verification
- **Rate Limiting**: Security mechanism to prevent excessive requests from a single source
- **Read Receipt**: Indicator showing when a message has been read by recipient
- **Typing Indicator**: Real-time notification showing when another user is typing

## Requirements

### Requirement 1

**User Story:** As a new user, I want to register using my IIT Indore email address, so that I can access the platform while maintaining exclusivity to the institute community.

#### Acceptance Criteria

1. WHEN a user submits a registration form with an email address, THEN the Ano System SHALL validate that the email domain is exactly "@iiti.ac.in"
2. WHEN a user submits a valid institute email, THEN the Ano System SHALL send a verification link to that email address
3. WHEN a user clicks the verification link, THEN the Ano System SHALL activate the account and allow profile creation
4. WHEN a user attempts to register with a non-institute email, THEN the Ano System SHALL reject the registration and display an error message
5. WHEN a user submits registration data, THEN the Ano System SHALL hash the password using Argon2 or bcrypt before storage

### Requirement 2

**User Story:** As a registered user, I want to authenticate securely using JWT tokens, so that my session remains secure and protected from unauthorized access.

#### Acceptance Criteria

1. WHEN a user logs in with valid credentials, THEN the Ano System SHALL generate both an access token and a refresh token
2. WHEN the Ano System generates tokens, THEN the Ano System SHALL store the refresh token in a secure HTTP-only cookie
3. WHEN a user makes an authenticated request, THEN the Ano System SHALL validate the access token and verify its signature
4. WHEN an access token expires, THEN the Ano System SHALL use the refresh token to generate a new access token
5. WHEN the Ano System detects multiple failed login attempts from the same source, THEN the Ano System SHALL implement rate limiting to prevent brute-force attacks

### Requirement 3

**User Story:** As a verified user, I want to create an anonymous profile with my interests and preferences, so that I can participate in matchmaking while keeping my identity private.

#### Acceptance Criteria

1. WHEN a user creates a profile, THEN the Ano System SHALL assign a unique anonymous identifier using UUID
2. WHEN a user submits profile data, THEN the Ano System SHALL store interests, hobbies, age, relationship intent, and personality tags without linking to real identity
3. WHEN a user uploads a profile picture, THEN the Ano System SHALL apply anonymity filters to prevent identity recognition
4. WHEN profile data is retrieved, THEN the Ano System SHALL never expose the user's institute email or real name
5. WHEN a user updates their profile, THEN the Ano System SHALL validate all input data on the server side

### Requirement 4

**User Story:** As a platform user, I want to join anonymous public chatrooms, so that I can communicate with other students without revealing my identity.

#### Acceptance Criteria

1. WHEN a user enters a chatroom, THEN the Ano System SHALL display the user with an anonymous identifier instead of their real name
2. WHEN a user sends a message in a chatroom, THEN the Ano System SHALL broadcast the message to all chatroom participants in real-time using WebSockets
3. WHEN a user sends an image or voice note, THEN the Ano System SHALL compress the media before storage and transmission
4. WHEN a user deletes or edits a message, THEN the Ano System SHALL update the message state for all chatroom participants
5. WHEN a user pins a message, THEN the Ano System SHALL mark the message as pinned and display it prominently in the chatroom

### Requirement 5

**User Story:** As a chatroom participant, I want to see real-time indicators like typing status and read receipts, so that I can have a natural conversation experience similar to WhatsApp.

#### Acceptance Criteria

1. WHEN a user types a message, THEN the Ano System SHALL broadcast a typing indicator to other chatroom participants via WebSocket
2. WHEN a user reads a message, THEN the Ano System SHALL send a read receipt to the message sender
3. WHEN a user comes online, THEN the Ano System SHALL update the user's online status for other participants while maintaining anonymity
4. WHEN a user reacts to a message, THEN the Ano System SHALL store the reaction and display it to all chatroom participants
5. WHEN a chatroom loads, THEN the Ano System SHALL implement infinite scroll to load older messages progressively

### Requirement 6

**User Story:** As a chatroom administrator, I want to send broadcast messages and moderate content, so that I can maintain order and communicate important information.

#### Acceptance Criteria

1. WHEN an administrator sends a broadcast message, THEN the Ano System SHALL deliver the message to all chatroom participants with admin designation
2. WHEN the Ano System detects inappropriate content, THEN the Ano System SHALL flag the message for review using auto-moderation algorithms
3. WHEN a user is reported multiple times, THEN the Ano System SHALL notify administrators for manual review

### Requirement 7

**User Story:** As a user seeking connections, I want to swipe through anonymous profiles in a Tinder-style interface, so that I can find potential matches based on shared interests.

#### Acceptance Criteria

1. WHEN a user opens the matchmaking interface, THEN the Ano System SHALL display anonymous profile cards with interests, hobbies, age, relationship intent, and personality tags
2. WHEN a user swipes left on a profile, THEN the Ano System SHALL record the rejection and show the next profile
3. WHEN a user swipes right on a profile, THEN the Ano System SHALL record the interest and check for mutual match
4. WHEN both users swipe right on each other, THEN the Ano System SHALL create a match and enable anonymous chat between them
5. WHEN displaying profiles, THEN the Ano System SHALL never show profiles that the user has already swiped on

### Requirement 8

**User Story:** As a matched user, I want to chat anonymously with my match, so that I can get to know them while maintaining privacy.

#### Acceptance Criteria

1. WHEN a match is created, THEN the Ano System SHALL open an anonymous chat window between the two users
2. WHEN a user sends a message in a matched chat, THEN the Ano System SHALL deliver the message in real-time using WebSockets
3. WHEN a user sends an image in a matched chat, THEN the Ano System SHALL apply anonymity masking to prevent identity revelation
4. WHEN a user types in a matched chat, THEN the Ano System SHALL show a typing indicator to the other user
5. WHEN a user reads a message in a matched chat, THEN the Ano System SHALL send a read receipt to the sender

### Requirement 9

**User Story:** As a platform user, I want to report or block other users, so that I can protect myself from harassment or inappropriate behavior.

#### Acceptance Criteria

1. WHEN a user reports another user, THEN the Ano System SHALL create a report record with the reporter's anonymous identifier and the reported user's anonymous identifier
2. WHEN a user blocks another user, THEN the Ano System SHALL prevent all future communication between the two users
3. WHEN a report is submitted, THEN the Ano System SHALL notify administrators without revealing the reporter's real identity
4. WHEN a user is blocked, THEN the Ano System SHALL hide the blocked user's profile from matchmaking results
5. WHEN multiple reports are received for the same user, THEN the Ano System SHALL escalate the case for administrative action

### Requirement 10

**User Story:** As a user, I want to search through my message history, so that I can find specific conversations or information quickly.

#### Acceptance Criteria

1. WHEN a user enters a search query, THEN the Ano System SHALL search through all messages in the user's accessible chats
2. WHEN search results are returned, THEN the Ano System SHALL highlight the matching text in the message preview
3. WHEN a user clicks a search result, THEN the Ano System SHALL navigate to that message in the chat history
4. WHEN searching, THEN the Ano System SHALL only return results from chats the user has access to

### Requirement 11

**User Story:** As a user, I want to use the application in both light and dark modes, so that I can choose the theme that suits my preference and environment.

#### Acceptance Criteria

1. WHEN a user toggles the theme, THEN the Ano System SHALL switch between light and dark color schemes
2. WHEN the theme changes, THEN the Ano System SHALL persist the user's preference in local storage
3. WHEN a user returns to the application, THEN the Ano System SHALL load the previously selected theme
4. WHEN the theme is applied, THEN the Ano System SHALL ensure all UI components are readable and accessible

### Requirement 12

**User Story:** As a security-conscious user, I want the platform to protect against common web vulnerabilities, so that my data and account remain secure.

#### Acceptance Criteria

1. WHEN the Ano System receives API requests, THEN the Ano System SHALL validate all input data on the server side
2. WHEN the Ano System handles authentication, THEN the Ano System SHALL implement CSRF protection mechanisms
3. WHEN the Ano System stores sensitive data, THEN the Ano System SHALL encrypt data at rest
4. WHEN the Ano System transmits data, THEN the Ano System SHALL use HTTPS for all communications
5. WHEN the Ano System processes file uploads, THEN the Ano System SHALL validate file types and scan for malicious content

### Requirement 13

**User Story:** As a platform user, I want the application to be responsive across all devices, so that I can use it seamlessly on desktop, tablet, or mobile.

#### Acceptance Criteria

1. WHEN a user accesses the application on any device, THEN the Ano System SHALL render a responsive layout optimized for that screen size
2. WHEN the viewport size changes, THEN the Ano System SHALL adjust the layout without losing functionality
3. WHEN touch gestures are used on mobile, THEN the Ano System SHALL respond appropriately to swipes, taps, and scrolls
4. WHEN the application loads on mobile, THEN the Ano System SHALL optimize media loading for bandwidth efficiency

### Requirement 14

**User Story:** As a developer, I want the system to maintain complete anonymity through UUID-based identifiers, so that no user identity can be leaked through the application.

#### Acceptance Criteria

1. WHEN the Ano System creates any user-facing identifier, THEN the Ano System SHALL use UUID format instead of sequential IDs
2. WHEN the Ano System stores relationships between users, THEN the Ano System SHALL use anonymous identifiers without linking to institute emails
3. WHEN the Ano System logs events, THEN the Ano System SHALL use anonymous identifiers in all log entries
4. WHEN the Ano System exposes data through APIs, THEN the Ano System SHALL never include institute email or real name in responses
5. WHEN database queries are executed, THEN the Ano System SHALL ensure proper indexing on UUID fields for performance

### Requirement 15

**User Story:** As an administrator, I want access to a dashboard for managing reports and monitoring platform health, so that I can maintain a safe and functional community.

#### Acceptance Criteria

1. WHEN an administrator logs into the admin dashboard, THEN the Ano System SHALL display pending reports with anonymous user identifiers
2. WHEN an administrator reviews a report, THEN the Ano System SHALL provide context about the reported behavior without revealing real identities
3. WHEN an administrator takes action on a report, THEN the Ano System SHALL record the action and update the user's status
4. WHEN the dashboard loads, THEN the Ano System SHALL display platform health metrics including active users and message volume
