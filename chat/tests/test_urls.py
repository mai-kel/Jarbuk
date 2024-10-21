from django.test import SimpleTestCase
from django.urls import resolve, reverse
from chat import views

class TestUrls(SimpleTestCase):

        def test_list_chats_url_resolves(self):
            url = reverse('chat:list_chats')
            self.assertEquals(resolve(url).func, views.list_chats)

        def test_get_private_chat_url_resolves(self):
            url = reverse('chat:get_private_chat', args=[1234])
            self.assertEquals(resolve(url).func, views.get_rendered_private_chat)

        def test_get_group_chat_url_resolves(self):
            url = reverse('chat:get_group_chat', args=[1234])
            self.assertEquals(resolve(url).func, views.get_rendered_group_chat)

        def test_get_private_message_url_resolves(self):
            url = reverse('chat:get_private_message', args=[1234])
            self.assertEquals(resolve(url).func, views.get_rendered_private_message)

        def test_get_group_message_url_resolves(self):
            url = reverse('chat:get_group_message', args=[1234])
            self.assertEquals(resolve(url).func, views.get_rendered_group_message)

        def test_create_group_chat_url_resolves(self):
            url = reverse('chat:create_group_chat')
            self.assertEquals(resolve(url).func, views.create_group_chat)

        def test_get_group_chat_info_url_resolves(self):
            url = reverse('chat:get_group_chat_info', args=[1234])
            self.assertEquals(resolve(url).func, views.get_group_chat_info)

        def test_get_add_users_page_url_resolves(self):
            url = reverse('chat:get_add_users_page', args=[1234])
            self.assertEquals(resolve(url).func, views.get_add_users_page)

        def test_add_user_to_group_chat_url_resolves(self):
            url = reverse('chat:add_user_to_group_chat')
            self.assertEquals(resolve(url).func, views.add_user_to_group_chat)

        def test_get_manage_group_page_url_resolves(self):
            url = reverse('chat:manage_group_chat', args=[1234])
            self.assertEquals(resolve(url).func, views.get_manage_group_page)

        def test_remove_user_from_group_chat_url_resolves(self):
            url = reverse('chat:remove_user_from_group_chat')
            self.assertEquals(resolve(url).func, views.remove_user_from_group_chat)

        def test_remove_from_admins_url_resolves(self):
            url = reverse('chat:remove_from_admins')
            self.assertEquals(resolve(url).func, views.remove_from_admins)

        def test_add_admin_to_group_chat_url_resolves(self):
            url = reverse('chat:add_admin_to_group_chat')
            self.assertEquals(resolve(url).func, views.add_admin_to_group_chat)

        def test_change_chat_image_url_resolves(self):
            url = reverse('chat:change_chat_image')
            self.assertEquals(resolve(url).func, views.change_chat_image)

        def test_change_chat_name_url_resolves(self):
            url = reverse('chat:change_chat_name')
            self.assertEquals(resolve(url).func, views.change_chat_name)

        def test_transfer_ownership_url_resolves(self):
            url = reverse('chat:transfer_ownership')
            self.assertEquals(resolve(url).func, views.transfer_ownership)

        def test_delete_group_chat_url_resolves(self):
            url = reverse('chat:delete_group_chat')
            self.assertEquals(resolve(url).func, views.delete_group_chat)

        def test_leave_group_chat_url_resolves(self):
            url = reverse('chat:leave_group_chat')
            self.assertEquals(resolve(url).func, views.leave_group_chat)

        def test_get_group_chat_messages_url_resolves(self):
            url = reverse('chat:get_group_chat_messages', args=[1234])
            self.assertEquals(resolve(url).func, views.get_paginated_group_chat_messages)

        def test_get_group_chat_messages_cursor_given_url_resolves(self):
            url = reverse('chat:get_group_chat_messages_before_id_given', args=[1234, 'cursor'])
            self.assertEquals(resolve(url).func, views.get_paginated_group_chat_messages)

        def test_get_private_chat_messages_url_resolves(self):
            url = reverse('chat:get_private_chat_messages', args=[1234])
            self.assertEquals(resolve(url).func, views.get_paginated_private_chat_messages)

        def test_get_private_chat_messages_cursor_given_url_resolves(self):
            url = reverse('chat:get_private_chat_messages_before_id_given', args=[1234, 'cursor'])
            self.assertEquals(resolve(url).func, views.get_paginated_private_chat_messages)