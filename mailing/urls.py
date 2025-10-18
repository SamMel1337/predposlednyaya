from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views


app_name = "mailing"

urlpatterns = [
    path("", views.MailingListView.as_view(), name="mailing_list"),
    path("create/", views.MailingCreateView.as_view(), name="mailing_create"),
    path("update/<int:pk>/", views.MailingUpdateView.as_view(), name="mailing_update"),
    path("delete/<int:pk>/", views.MailingDeleteView.as_view(), name="mailing_delete"),
    path("detail/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"),
    path("send/<int:pk>/", views.SendMailingView.as_view(), name="mailing_send"),
    path("messages/", views.MessageListView.as_view(), name="message_list"),
    path("messages/create/", views.MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/update/<int:pk>/",
        views.MessageUpdateView.as_view(),
        name="message_update",
    ),
    path(
        "messages/delete/<int:pk>/",
        views.MessageDeleteView.as_view(),
        name="message_delete",
    ),
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/create/", views.ClientCreateView.as_view(), name="client_create"),
    path(
        "clients/update/<int:pk>/",
        views.ClientUpdateView.as_view(),
        name="client_update",
    ),
    path(
        "clients/delete/<int:pk>/",
        views.ClientDeleteView.as_view(),
        name="client_delete",
    ),
    path("attempts/", views.MailingAttemptListView.as_view(), name="attempt_list"),
    path("statistics/", views.StatisticsView.as_view(), name="statistics"),
    path(
        "disable/<int:pk>/", views.DisableMailingView.as_view(), name="disable_mailing"
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
