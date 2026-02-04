from django.contrib import admin
from .models import Chatroom, Message, MessageReaction, ReadReceipt


@admin.register(Chatroom)
class ChatroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'member_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'chatroom', 'message_type', 'is_deleted', 'is_pinned', 'created_at']
    list_filter = ['message_type', 'is_deleted', 'is_pinned', 'created_at']
    search_fields = ['content']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['message', 'profile', 'emoji', 'created_at']
    list_filter = ['emoji', 'created_at']
    readonly_fields = ['id', 'created_at']


@admin.register(ReadReceipt)
class ReadReceiptAdmin(admin.ModelAdmin):
    list_display = ['message', 'profile', 'read_at']
    list_filter = ['read_at']
    readonly_fields = ['id', 'read_at']
