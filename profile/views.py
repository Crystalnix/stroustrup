from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from book_library.views import LoginRequiredView
import forms


class ProfileView(LoginRequiredView, DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.get_profile().library != self.request.user.get_profile().library:
            return HttpResponseRedirect(reverse('books:users'))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, object):
        context = {'profile': object, 'books': object.get_users_books()}
        return super(ProfileView, self).get_context_data(**context)


@csrf_protect
@login_required
def profile_change(request):

    template_name = 'profile_change.html'
    profile_change_form = forms.ProfileForm
    post_change_redirect = reverse("profile:profile", args=str(request.user.pk))
    if request.method == "POST":
        form = profile_change_form(user=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
        else:
            context = {'form': form}
            return TemplateResponse(request, template_name, context)
    else:
        form = profile_change_form(user=request.user)
        context = {'form': form}
        return TemplateResponse(request, template_name, context)



