from types import TupleType
import random
import string

from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from django.contrib.auth import authenticate

from testbase import create_random_user, write_percentage, count_delta, random_string

from book_library.views import *


MAX_NUMBER_OF_AUTHORS = 50

MAX_NUMBER_OF_BOOKS = 50

MAX_NUMBER_OF_TAGS = 50

NUMBER_OF_ITERATIONS_A_T_R = 50  # in ask/take/return tests

NUMBER_OF_ITERATIONS_BOOKS = 250  # in add book tests

NUMBER_OF_ITERATIONS_AUTHORS = 500

NUMBER_OF_ITERATIONS_TAGS = 500

NUMBER_OF_ITERATIONS_SEARCH = 30

MAX_LENGTH_OF_DESCRIPTION = 1000

MAX_LENGTH_OF_AUTHORS = 90

MAX_LENGTH_OF_TAGS = 250


def get_success_authors_string():
    number_of_authors = random.randint(1, MAX_LENGTH_OF_AUTHORS // 3)  # 3 cause a shortest author is a_b
    max_average_length = MAX_LENGTH_OF_AUTHORS // number_of_authors
    list_of_authors = list()
    for item in range(0, number_of_authors):
        random_author_first_name = random_string(random.randint(1, max_average_length-2),  chars=string.letters)
        random_number_of_spaces = random_string(random.randint(1, max_average_length-len(random_author_first_name)),
                                                chars=" ")
        random_author_last_name = random_string(random.randint(1, 1+max_average_length -
                                                                  (len(random_number_of_spaces) +
                                                                   len(random_author_first_name))),
                                                chars=string.letters)
        list_of_authors.append(random_author_first_name+random_number_of_spaces+random_author_last_name + ',')
    return ''.join(list_of_authors)


class RestrictionsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        for i in range(1, random.randint(1, MAX_NUMBER_OF_AUTHORS)):
            author = Author.authors.create(first_name='John'+str(i), last_name='Doe'+str(i))
        for i in range(1, random.randint(1, MAX_NUMBER_OF_BOOKS)):
            book = Book.books.create(title='test_book'+str(i))
        for i in range(1, random.randint(1, MAX_NUMBER_OF_TAGS)):
            tag = Book_Tag.tags.create(tag='test_tag'+str(i))
        urls_to_test = ['books:list', 'books:add', 'books:add_tag', 'books:add_author']
        for book in Book.books.all():
            urls_to_test.append(('books:book', book.pk))
            urls_to_test.append(('books:take', book.pk))
            urls_to_test.append(('books:ask', book.pk))
            urls_to_test.append(('books:return', book.pk))
            urls_to_test.append(('books:change', book.pk))
            urls_to_test.append(('books:delete', book.pk))
            urls_to_test.append(('books:story', book.pk))
        self.urls_to_test = urls_to_test

    def test_availability(self):
        delta_percent = count_delta(len(self.urls_to_test))
        percentage = delta_percent
        for url in self.urls_to_test:
            percentage = write_percentage(percentage, delta_percent)
            if type(url) is TupleType:
                urln = url[0]
                urlp = url[1]
                request = self.client.get(reverse(urln, kwargs={'pk': urlp}))
            else:
                urln = url
                request = self.client.get(reverse(urln))
            self.assertTrue(request.status_code != 404)

    def test_logged_out_rights(self):
        delta_percent = count_delta(len(self.urls_to_test))
        percentage = delta_percent
        for url in self.urls_to_test:
            percentage = write_percentage(percentage, delta_percent)
            if type(url) is TupleType:
                urln = url[0]
                urlp = url[1]
                request = self.client.get(reverse(urln, kwargs={'pk': urlp}))
            else:
                urln = url
                request = self.client.get(reverse(urln))
            self.assertTrue(request['location'].startswith('http://testserver/auth/login?next='))

    def test_user_rights(self):
        restricted_urls = [x for x in self.urls_to_test
                           if x in ('books:add', 'books:add_tag', 'books:add_author') or
                              (type(x) is TupleType and x[0] in ('books:delete', 'books:change'))]
        allowed_urls = list(set(self.urls_to_test) - set(restricted_urls))
        user = create_random_user()
        self.client.login(username=user[0].username, password=user[1])
        delta_percent = count_delta(len(self.urls_to_test))
        percentage = delta_percent
        for url in allowed_urls:
            percentage = write_percentage(percentage, delta_percent)
            if type(url) is TupleType:
                urln = url[0]
                urlp = url[1]
                request = self.client.get(reverse(urln, kwargs={'pk': urlp}))
            else:
                urln = url
                request = self.client.get(reverse(urln))
            if request.status_code == 200:
                self.assertEqual(request.status_code, 200)
            else:
                self.assertTrue(not request['location'].startswith('http://testserver/auth/login?next='))
        for url in restricted_urls:
            percentage = write_percentage(percentage, delta_percent)
            if type(url) is TupleType:
                urln = url[0]
                urlp = url[1]
                request = self.client.get(reverse(urln, kwargs={'pk': urlp}))
            else:
                urln = url
                request = self.client.get(reverse(urln))
            self.assertEqual(request.status_code, 302)

    def test_admin_rights(self):
        user = create_random_user()
        user[0].is_staff = True
        user[0].save()
        authenticate(username=user[0].username, password=user[1])
        self.client.login(username=user[0].username, password=user[1])
        delta_percent = count_delta(len(self.urls_to_test))
        percentage = delta_percent
        for url in self.urls_to_test:
            percentage = write_percentage(percentage, delta_percent)
            if type(url) is TupleType:
                urln = url[0]
                urlp = url[1]
                request = self.client.get(reverse(urln, kwargs={'pk': urlp}))
            else:
                urln = url
                request = self.client.get(reverse(urln))
            if request.status_code == 200:
                self.assertEqual(request.status_code, 200)
            else:
                self.assertTrue(not request['location'].startswith('http://testserver/auth/login?next='))


class FormsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        admin = create_random_user()
        self.admin = admin[0]
        self.admin.is_staff = True
        self.admin.save()
        self.client.login(username=admin[0].username, password=admin[1])

    def test_add_book(self):
        books_count = 0
        delta_percent = count_delta(NUMBER_OF_ITERATIONS_BOOKS)
        percentage = delta_percent
        for i in range(1, NUMBER_OF_ITERATIONS_BOOKS):
            percentage = write_percentage(percentage, delta_percent)
            there_is_isbn = random.randint(0, 1)
            will_be_an_error = random.randint(0, 1)
            was_error = False
            isbn = None
            if there_is_isbn:
                if will_be_an_error and random.randint(0, 1):  # it will be in this field
                    while True:
                        isbn = random_string(random.randint(1, 50), chars=string.digits)
                        if len(isbn) == 13 and isbn.isdigit():
                            continue
                        was_error = True
                        break
                else:
                    isbn = random_string(13, chars=string.digits)
            if will_be_an_error and random.randint(0, 1):  # it will be in this field
                title = random_string(size=(random.randint(46, 100)))
                was_error = True
            else:
                title = random_string(size=(random.randint(1, 45)))
            e_version_exists = 0
            paperback_version_exists = random.randint(0, 1)
            # if e_version_exists == 0:
            #     book_file = None
            # else:
            #     book_file = File('test_file.txt')
            description = random_string(size=random.randint(1, MAX_LENGTH_OF_DESCRIPTION), chars=string.printable)
            if will_be_an_error and (random.randint(0, 1) or not was_error):
                authors = random_string(size=random.randint(1, 90), chars=string.letters)
            else:
                authors = get_success_authors_string()
            # if will_be_an_error and (random.randint(0, 1) or not was_error):
            #     tags = random_string(size=random.randint(1, 90), chars=string.letters)
            # else:
            #     tags = random_string(size=random.randint(1, MAX_LENGTH_OF_TAGS), chars=string.printable)
            form_context = {'title': title,
                            'e_version_exists': e_version_exists,
                            'paperback_version_exists': paperback_version_exists,
                            'description': description,
                            'file': None,
                            'authors_names': authors}
            if there_is_isbn:
                form_context['isbn'] = isbn
            response = self.client.post(reverse('books:add'), form_context)
            if not will_be_an_error:
                books_count += 1
                self.assertEqual(response.status_code, 200)
                new_book = Book.books.get(pk=books_count)
                self.assertEqual(new_book.title, title)
                self.assertEqual(new_book.description, description)
                if there_is_isbn:
                    self.assertEqual(new_book.isbn, isbn)
            else:
                self.assertTrue(not response.context_data['form'].is_valid())

    def test_search(self):
        tags_count = 0
        delta_percent = count_delta(NUMBER_OF_ITERATIONS_SEARCH)
        percentage = delta_percent
        for i in range(1, NUMBER_OF_ITERATIONS_SEARCH):
            percentage = write_percentage(percentage, delta_percent)
            book_free = Book.books.create(title='BUGABUGA')
            book_busy = Book.books.create(title='BUGABUGA')
            book_busy.busy = True
            book_busy.save()
            will_be_an_error = random.randint(0, 1)
            if will_be_an_error:
                while True:
                        tags = random_string(size=(random.randint(70, 100)))
                        if' BUGABUGA ' in tags:
                            continue
                        was_error = True
                        break
            else:
                tags = random_string(size=(random.randint(0, 80-len(' BUGABUGA '))))
                position = random.randint(0, len(tags))
                tags = tags[:position] + ' BUGABUGA ' + tags[position:]
            request = self.client.get(reverse('books:list'), {'keywords': tags})
            if not will_be_an_error:
                book_busy = Book.books.get(pk=2)
                book_free = Book.books.get(pk=1)
                self.assertTrue(book_free in request.context_data['object_list'] and book_busy in request.context_data['object_list'])
                request = self.client.get(reverse('books:list'), {'keywords': tags, 'busy': '1'})
                book_busy = Book.books.get(pk=2)
                book_free = Book.books.get(pk=1)
                self.assertTrue(book_free in request.context_data['object_list'] and book_busy not in request.context_data['object_list'])
                request = self.client.get(reverse('books:list'), {'keywords': tags, 'busy': '2'})
                book_busy = Book.books.get(pk=2)
                book_free = Book.books.get(pk=1)
                self.assertTrue(book_free not in request.context_data['object_list'] and book_busy in request.context_data['object_list'])


class SpecialCaseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_take_return_ask_successfully(self):
        user1 = create_random_user()
        user2 = create_random_user()
        delta_percent = count_delta(NUMBER_OF_ITERATIONS_A_T_R)
        percentage = delta_percent
        for i in range(1, NUMBER_OF_ITERATIONS_A_T_R):
            percentage = write_percentage(percentage, delta_percent)
            book = Book.books.create(title='test_book'+str(i))
                # first_user asks free book
            self.client.login(username=user1[0].username, password=user1[1])
            request = self.client.get(reverse("books:ask", kwargs={'pk': book.pk}))
            self.assertEqual(request.status_code, 302)
            self.assertTrue(request['location'] == "http://testserver/books/")  # You can't ask free book
                # and take it
            request = self.client.get(reverse("books:take", kwargs={'pk': book.pk}))
            self.assertTrue(request['location'] == "http://testserver/books/")  # You can take free book
                # book really taken by him
            book = Book.books.get(pk=i)
            self.assertTrue(book.busy and book in user1[0].get_users_books())
                # second user logs in
            self.client.logout()
            self.client.login(username=user2[0].username, password=user2[1])
                # and tried to take busy book
            request = self.client.get(reverse("books:take", kwargs={'pk': book.pk}))
            self.assertEqual(request.status_code, 302)
            self.assertEqual(request['location'], "http://testserver/books/")  # You can't take busy book
            book = Book.books.get(pk=i)
            self.assertTrue(book not in user2[0].get_users_books())
                # and to return
            request = self.client.get(reverse("books:return", kwargs={'pk': book.pk}))
            self.assertEqual(request.status_code, 302)
            self.assertEqual(request['location'], "http://testserver/books/")  # You can't return busy (not yours) book
            book = Book.books.get(pk=i)
            self.assertTrue(book.busy and book in user1[0].get_users_books())
                # he asks this book
            request = self.client.get(reverse("books:ask", kwargs={'pk': book.pk}))
            self.assertEqual(request.status_code, 200)  # You can ask busy book
                # and secondone logs in
            self.client.logout()
            self.client.login(username=user1[0].username, password=user1[1])
                # he returns book and book is returned
            request = self.client.get(reverse("books:return", kwargs={'pk': book.pk}))
            self.assertEqual(request['location'], "http://testserver/books/")  # You can return book
            book = Book.books.get(pk=i)
            self.assertTrue(not book.busy and book not in user1[0].get_users_books())
                # first user logs in
            self.client.logout()
            self.client.login(username=user2[0].username, password=user2[1])
                # takes book
            request = self.client.get(reverse("books:take", kwargs={'pk': book.pk}))
            self.assertEqual(request['location'], "http://testserver/books/")
            book = Book.books.get(pk=i)
            self.assertTrue(book.busy and (book in user2[0].get_users_books()))  # You can take free book after it was taken
                # looks at it in his profile
            request = self.client.get(reverse("profile:profile", kwargs={'pk': user2[0].pk}))
            self.assertEqual(request.status_code, 200)
                # and returns it
            request = self.client.get(reverse("books:return", kwargs={'pk': book.pk}))
            self.assertEqual(request['location'], "http://testserver/books/")
            book = Book.books.get(pk=i)
            books = user2[0].get_users_books()
            self.assertTrue(not book.busy and (book not in user2[0].get_users_books()))

            self.client.logout()

    # def test_request_book_post(self):

