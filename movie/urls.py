from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logOut', views.logOut, name='logOut'),
    path('get_movie/', views.get_movie, name='get_movie'),
    path('fetch/<int:id>/<str:text>/', views.fetch, name='fetch'),
    path('wishlist/<int:id>/<str:type>/', views.add_to_list, name='add_to_list'),
    path('watchlist/<str:type>/', views.watchlist, name='watchlist'),
    path('remove_from_watchlist/<int:uni>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('change_watchlist/<int:uni>/<str:type>', views.change_watchlist, name='change'),
    path('recommend_by_genre/', views.recommend_by_genre, name='recommend_by_genre'),
    path('recommend/', views.recommend, name='recommend')
]