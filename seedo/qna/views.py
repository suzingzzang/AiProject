from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.edit import FormView

from .forms import CommentForm, QnAForm
from .models import QnA


class QnAListView(LoginRequiredMixin, ListView):
    model = QnA
    template_name = "qna_list.html"
    context_object_name = "questions"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return QnA.objects.all()
        else:
            return QnA.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"] = "list"
        return context


class QnADetailView(View):
    def get(self, request, pk):
        question = get_object_or_404(QnA, pk=pk)
        comment_form = CommentForm()
        comments_list = question.comments.split("\n") if question.comments else []
        context = {"question": question, "comment_form": comment_form, "comments_list": comments_list}
        return render(request, "qna_detail.html", context)

    def post(self, request, pk):
        question = get_object_or_404(QnA, pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data["content"]
            if question.comments:
                question.comments += f"\n{comment}"
            else:
                question.comments = comment
            question.save()

        return redirect("qna-detail", pk=pk)


def comment_update(request, pk):
    question = get_object_or_404(QnA, pk=pk)

    if question.comments:

        question.comments = f"{request.user.email}: {request.POST['content']}"
    else:
        question.comments = f"{request.user.email}: {request.POST['content']}"

    question.save()

    return redirect("qna-detail", pk=pk)


def comment_delete(request, pk):
    question = get_object_or_404(QnA, pk=pk)

    question.comments = ""
    question.save()

    return redirect("qna-detail", pk=pk)


class QnACreateView(LoginRequiredMixin, CreateView):
    model = QnA
    form_class = QnAForm
    template_name = "qna_form.html"
    success_url = "/qna/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"] = "form"
        return context


class QnAUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = QnA
    form_class = QnAForm
    template_name = "qna_form.html"
    success_url = "/qna/"

    def test_func(self):
        question = self.get_object()
        return self.request.user.is_superuser or self.request.user == question.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"] = "form"
        return context


class QnADeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = QnA
    template_name = "qna_confirm_delete.html"
    success_url = "/qna/"

    def test_func(self):
        question = self.get_object()
        return self.request.user.is_superuser or self.request.user == question.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"] = "delete"
        return context


class CommentCreateView(FormView):
    template_name = "qna_detail.html"
    form_class = CommentForm

    def form_valid(self, form):
        question = get_object_or_404(QnA, pk=self.kwargs["pk"])

        if question.comments:
            question.comments += f"\n{self.request.user.email}: {form.cleaned_data['content']}"
        else:
            question.comments = f"{self.request.user.email}: {form.cleaned_data['content']}"

        question.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("qna-detail", kwargs={"pk": self.kwargs["pk"]})
