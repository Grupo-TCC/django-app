from . import views_message_api
from django.urls import path
from . import views
from . import views_message_api
from .delete_article_view import delete_article

app_name = 'feed'

urlpatterns = [
    path("follow/<int:user_id>/", views.toggle_follow, name="toggle_follow"),
    path("conexao/", views.conexao, name="conexao"),
    path("settings/", views.settings_view, name="settings"),
    path("artigos/", views.artigos, name="artigos"),
    path("verificacao/", views.verificacao, name="verificacao"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/<int:user_id>/", views.perfil, name="perfil"),
    path("community/", views.community, name="community"),
    path("community/<int:community_id>/", views.community_detail, name="community_detail"),
    path("article/<int:article_id>/delete/", delete_article, name="delete_article"),
    # path("verificacao/submit/", views.submit_verificacao, name="submit_verificacao"),
    path("mensagens/", views.mensagens, name="mensagens"),
    path("mensagens/api/get_messages/", views_message_api.get_messages_api, name="get_messages_api"),
    path("mensagens/api/send_message/", views_message_api.send_message_api, name="send_message_api"),
    path("traducao/", views.media_post, name="media_post"),
    path("media/<int:media_id>/request-access/", views.request_media_access, name="request_media_access"),
    path("media/<int:media_id>/like/", views.toggle_media_like, name="toggle_media_like"),
    path("media/<int:media_id>/comment/", views.add_media_comment, name="add_media_comment"),
    path("media/<int:media_id>/comments/", views.get_media_comments, name="get_media_comments"),
    path("produtos/", views.produtos, name="produtos"),
]