import os
import sys
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from reputation.models import UserReputation
from profiles.models import Profile

User = get_user_model()

users_data = [
    # {"email": "cse220001001@iiti.ac.in", "score": 150, "tier": "Sophomore"},
    # {"email": "cse220001002@iiti.ac.in", "score": 600, "tier": "Senior"},
    # {"email": "cse220001003@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
     {"email": "cse220001004@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
      {"email": "cse220001005@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
       {"email": "cse220001006@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
        {"email": "cse220001007@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
         {"email": "cse220001008@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
          {"email": "cse220001009@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
           {"email": "cse220001010@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
            {"email": "cse220001011@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
             {"email": "cse220001012@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
              {"email": "cse220001013@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
               {"email": "cse220001014@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
                {"email": "cse220001015@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
                 {"email": "cse220001016@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
                  {"email": "cse220001017@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
                   {"email": "cse220001018@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
                    {"email": "cse220001019@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
                     {"email": "cse220001020@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
                      {"email": "cse220001021@iiti.ac.in", "score": 1200, "tier": "Campus Legend"},
]

password = "TestPass123!"

for data in users_data:
    email = data["email"]
    score = data["score"]
    username = email.split('@')[0]
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User(email=email, username=username)
        
    user.set_password(password)
    if hasattr(user, 'is_verified'):
        user.is_verified = True
    user.is_active = True
    user.save()
    

    try:
        profile, p_created = Profile.objects.get_or_create(
            user=user
        )
    except Exception as e:
        print(f"Could not create profile for {email}: {e}")
    
    reputation, r_created = UserReputation.objects.get_or_create(user=user)
    reputation.reputation_score = score
    reputation.update_tier()
    reputation.save()
    
    print(f"Created user: {email} | Password: {password} | Tier: {reputation.rank_tier} | Score: {reputation.reputation_score}")

print("Done creating test users!")
