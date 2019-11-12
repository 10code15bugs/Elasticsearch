"""LcvSearch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.views.generic import TemplateView
from search.views import SearchSuggest,SearchView,IndexView
urlpatterns = [
    url(r'admin/', admin.site.urls),
    #url(r'^$', TemplateView.as_view(template_name="index.html"),name="index"),#默认view
    url(r'^$', IndexView.as_view(),name="index"),#自定义view
    url(r'^suggest/$', SearchSuggest.as_view(),name="suggest"),
    url(r'^search/$', SearchView.as_view(),name="search"),

    #url(r'^search/$', QuestionView.as_view(),name="question"),
    #url(r'^suggest/$', QuestionSuggest.as_view(),name="questionsuggest"),
    #url(r'^search/$', AnswerView.as_view(),name="answer"),

]
