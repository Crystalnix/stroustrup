from django.contrib import admin
from book_library.models import Book, Author, Book_Tag, Book_Request, Request_Return
from profile.models import Profile_addition
from main.models import FileStorage

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


class FileStorageAdmin(admin.ModelAdmin):
    model = FileStorage


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book_Tag, Book_TagAdmin)
admin.site.register(Book_Request, Book_RequestAdmin) #SpaTedition
admin.site.register(Profile_addition, Profile_additionsAdmin)
admin.site.register(Request_Return, Request_ReturnAdmin)
admin.site.register(FileStorage, FileStorageAdmin)

