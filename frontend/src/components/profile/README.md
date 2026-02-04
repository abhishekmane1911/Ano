# Profile System Frontend

This directory contains all frontend components for the anonymous profile system.

## Components

### ProfileCreation
Multi-step form for creating a new anonymous profile. Includes:
- Step 1: Basic information (age, relationship intent)
- Step 2: Interests & hobbies
- Step 3: Personality tags
- Step 4: Profile picture & bio

**Route:** `/profile/create`

### ProfileEditor
Component for editing an existing profile. Allows users to update:
- Profile picture
- Age and relationship intent
- Interests and hobbies
- Personality tags
- Bio

**Route:** `/profile/edit`

### InterestSelector
Reusable tag-based selector component with:
- Text input with suggestions dropdown
- Tag display with remove functionality
- Customizable suggestions list
- Used for interests, hobbies, and personality tags

### AnonymousAvatar
Profile picture component with:
- Image upload with preview
- File type validation (JPEG, PNG, GIF)
- File size validation (max 5MB)
- Placeholder for no image
- Hover overlay for editing
- Multiple size options (small, medium, large)

## API Integration

All components use the `profileAPI` from `src/api/profile.ts`:
- `createProfile()` - Create new profile
- `getMyProfile()` - Get current user's profile
- `updateMyProfile()` - Update profile data
- `uploadAvatar()` - Upload profile picture

## State Management

Profile state is managed using Zustand in `src/stores/profileStore.ts`:
- `profile` - Current profile data
- `isLoading` - Loading state
- `error` - Error messages
- `setProfile()` - Update profile
- `clearProfile()` - Clear profile data

## Validation

Client-side validation includes:
- Age: 18-100
- Interests: At least one required
- Hobbies: At least one required
- Personality tags: At least one required
- Bio: Optional, max 500 characters
- Avatar: Optional, JPEG/PNG/GIF, max 5MB

## Styling

All components use `ProfileComponents.css` with:
- Responsive design (mobile-first)
- Consistent color scheme matching auth components
- Smooth animations and transitions
- Accessible form controls

## Requirements Validation

This implementation satisfies:
- **Requirement 3.1**: Anonymous profile creation with UUID
- **Requirement 3.2**: Profile data storage (interests, hobbies, age, etc.)
- **Requirement 3.3**: Avatar upload with anonymity filters
- **Requirement 3.5**: Client-side validation for profile fields
