# Profile System Testing Guide

## Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend dev server running on `http://localhost:5173`
3. User authenticated with valid JWT token

## Testing Profile Creation

### Test Case 1: Create Profile - Happy Path
1. Navigate to `/profile/create`
2. **Step 1 - Basic Information:**
   - Enter age: 22
   - Select relationship intent: "Friendship"
   - Click "Next"
3. **Step 2 - Interests & Hobbies:**
   - Add interests: "Music", "Technology", "Reading"
   - Add hobbies: "Playing Guitar", "Coding", "Running"
   - Click "Next"
4. **Step 3 - Personality:**
   - Add personality tags: "Outgoing", "Creative", "Thoughtful"
   - Click "Next"
5. **Step 4 - Picture & Bio:**
   - Upload a profile picture (optional)
   - Enter bio: "Love music and tech. Always up for a good conversation!"
   - Click "Create Profile"
6. **Expected Result:** Profile created successfully, redirected to home page

### Test Case 2: Validation Errors
1. Navigate to `/profile/create`
2. **Step 1:**
   - Enter age: 15 (invalid)
   - Click "Next"
   - **Expected:** Error message "Age must be between 18 and 100"
3. **Step 2:**
   - Don't add any interests
   - Click "Next"
   - **Expected:** Error message "Please add at least one interest"

### Test Case 3: Avatar Upload Validation
1. Navigate to `/profile/create`
2. Complete steps 1-3
3. **Step 4:**
   - Try uploading a .txt file
   - **Expected:** Alert "Invalid file type. Only JPEG, PNG, and GIF are allowed"
   - Try uploading a 10MB image
   - **Expected:** Alert "File size too large. Maximum size is 5MB"

## Testing Profile Editor

### Test Case 4: Edit Existing Profile
1. Navigate to `/profile/edit`
2. **Expected:** Form pre-filled with existing profile data
3. Modify age to 23
4. Add new interest: "Photography"
5. Update bio
6. Click "Save Changes"
7. **Expected:** Success message "Profile updated successfully!"

### Test Case 5: Avatar Update
1. Navigate to `/profile/edit`
2. Click on avatar to upload new image
3. Select valid image file
4. **Expected:** Preview shows new image
5. Click "Save Changes"
6. **Expected:** Profile updated with new avatar

## Testing InterestSelector Component

### Test Case 6: Tag Management
1. In any profile form, focus on an interest input
2. Type "Mus" - **Expected:** Suggestions dropdown shows "Music"
3. Click suggestion - **Expected:** Tag added to selected items
4. Type "Custom Interest" and press Enter
5. **Expected:** Custom tag added
6. Click × on a tag - **Expected:** Tag removed

## API Integration Tests

### Test Case 7: Profile Creation API
```bash
# Ensure backend returns profile with anonymous_id
curl -X POST http://localhost:8000/api/profiles/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 22,
    "interests": ["Music", "Technology"],
    "hobbies": ["Coding", "Gaming"],
    "relationship_intent": "friendship",
    "personality_tags": ["Creative", "Analytical"],
    "bio": "Test bio"
  }'
```

### Test Case 8: Avatar Upload API
```bash
curl -X POST http://localhost:8000/api/profiles/avatar/ \
  -H "Authorization: Bearer <access_token>" \
  -F "avatar=@/path/to/image.jpg"
```

## Validation Checklist

- [ ] Age validation (18-100)
- [ ] At least one interest required
- [ ] At least one hobby required
- [ ] At least one personality tag required
- [ ] Bio max 500 characters
- [ ] Avatar file type validation
- [ ] Avatar file size validation (5MB)
- [ ] Multi-step navigation works
- [ ] Progress bar updates correctly
- [ ] Form data persists between steps
- [ ] Success/error messages display correctly
- [ ] Profile data loads in editor
- [ ] Profile updates save correctly
- [ ] Anonymous ID displayed in editor
- [ ] Responsive design on mobile
- [ ] All components styled consistently

## Known Limitations

1. **Anonymity Filters:** Avatar anonymity filters are mentioned in the UI but actual image processing happens on the backend
2. **Profile Picture Preview:** Preview shows original image before backend processing
3. **No Profile Check:** App doesn't automatically redirect to profile creation if user has no profile yet (future enhancement)

## Next Steps

After testing, consider:
1. Add profile completion check on login
2. Add profile view page (read-only)
3. Add profile deletion functionality
4. Implement actual anonymity filters for avatars
5. Add image cropping/editing before upload
