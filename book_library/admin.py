from django.contrib import admin
from book_library.models import Book, Author, Book_Tag, Book_Request, Request_Return, Library
from profile.models import Profile_addition, CustomUser
from profile.forms import CustomUserChangeForm
from invitation.models import Invite
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
# from django.contrib.auth.urls import


User = get_user_model()

class BooksInLine(admin.TabularInline):
    model = Book

class TagsInLine(admin.StackedInline):
    model = Book_Tag

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn')

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')

class Book_TagAdmin(admin.ModelAdmin):
    display = 'tag'
    #inlines = [TagsInLine]

class RequestsInLine(admin.TabularInline):
    model = Book_Request

class Book_RequestAdmin(admin.ModelAdmin): #SpaT edition
    list_display = ('title', 'url', 'vote')
    #inlines = [RequestsInLine]

class Profile_additionsAdmin(admin.ModelAdmin):
    model = Profile_addition
    list_display = ('user', 'avatar')

class Request_ReturnAdmin(admin.ModelAdmin):
    model = Request_Return
    list_display = ('user_request', 'book', 'time_request', 'processing_time')

class LibraryAdmin(admin.ModelAdmin):
    model = Library
    list_display = ('name',)


class InviteAdmin(admin.ModelAdmin):
    model = Invite
    list_display = ('email',)

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User


class CustomUserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('username', 'email', 'library', 'is_manager')
    form = CustomUserChangeForm
    change_password_form = AdminPasswordChangeForm


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book_Tag, Book_TagAdmin)
admin.site.register(Book_Request, Book_RequestAdmin) #SpaTedition
admin.site.register(Profile_addition, Profile_additionsAdmin)
admin.site.register(Request_Return, Request_ReturnAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(Invite, InviteAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
