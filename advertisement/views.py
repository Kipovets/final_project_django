from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView
from django.utils.translation import gettext_lazy as _

from .models import Advertisement, User
from .forms import AdvertisementForm, ReplyForm, RegistrationForm


class IndexView(TemplateView):
    template_name = 'index.html'


class Register(View):
    template_name = 'account/register.html'

    def get(self, request):
        context = {
            'form': RegistrationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('index')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)


class AdvertisementCreate(CreateView):
    form_class = AdvertisementForm
    model = Advertisement
    template_name = 'advertisement/create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = User.objects.get(id=self.request.user.id)
        return super().form_valid(form)


class AdvertisementView(ListView):
    model = Advertisement
    template_name = 'advertisement/list.html'
    ordering = '-time_create'
    context_object_name = 'post_list'


def advertisement_detail(request, post_id):
    post = get_object_or_404(Advertisement, pk=post_id)
    replies = post.replies.count
    new_reply = None
    if request.method == 'POST':
        reply_form = ReplyForm(data=request.POST)
        if reply_form.is_valid():
            new_reply = reply_form.save(commit=False)
            new_reply.post = post
            new_reply.user = User.objects.get(id=request.user.id)
            new_reply.save()
    else:
        reply_form = ReplyForm()
    return render(request, 'advertisement/post.html', {'post': post, 'replies': replies, 'new_reply': new_reply, 'reply_form': reply_form})



