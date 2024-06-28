from django.urls import path

from user_manage.views import UserManageView, UserDetailManageView, UserAvatarView, \
                            SelfView, SelfAvatarView, RegisertView, LoginView, LogoutView

urlpatterns = [
    path("manage", UserManageView.as_view()),
    path("manage/<id>", UserDetailManageView.as_view()),
    path("avatar/<id>", UserAvatarView.as_view()),
    path("self", SelfView.as_view()),
    path("self/avatar", SelfAvatarView.as_view()),
    path("register", RegisertView.as_view()),
    path("login", LoginView.as_view()),
    path("logout", LogoutView.as_view()),
    
]