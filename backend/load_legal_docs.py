"""
Script to load legal documents into the database
Run with: python manage.py shell < load_legal_docs.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ano_backend.settings')
django.setup()

from authentication.models_legal import LegalDocument
from django.utils import timezone

def load_legal_documents():
    """Load legal documents from markdown files"""
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    documents = [
        {
            'type': 'tos',
            'file': 'TERMS_OF_SERVICE.md',
            'version': '1.0'
        },
        {
            'type': 'privacy',
            'file': 'PRIVACY_POLICY.md',
            'version': '1.0'
        },
        {
            'type': 'guidelines',
            'file': 'COMMUNITY_GUIDELINES.md',
            'version': '1.0'
        }
    ]
    
    for doc_info in documents:
        file_path = os.path.join(base_dir, doc_info['file'])
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create or update document
        doc, created = LegalDocument.objects.update_or_create(
            document_type=doc_info['type'],
            version=doc_info['version'],
            defaults={
                'content': content,
                'effective_date': timezone.now(),
                'is_active': True
            }
        )
        
        action = "Created" if created else "Updated"
        print(f"✅ {action}: {doc.get_document_type_display()} v{doc.version}")

if __name__ == '__main__':
    print("Loading legal documents...")
    load_legal_documents()
    print("\n✅ All legal documents loaded successfully!")
    print("\nNext steps:")
    print("1. Review documents in Django admin")
    print("2. Test API endpoints: /api/auth/legal/documents/")
    print("3. Integrate with frontend")
